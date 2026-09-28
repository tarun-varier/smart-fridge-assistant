"""Fine-tune the MobileNetV2 head (backbone frozen) on the deduplicated
fresh/spoiled manifest, then evaluate on the held-out test split.

Run with the project venv: .venv/bin/python scripts/train_classifier.py
"""

import csv
import json
import sys
import time
from pathlib import Path

import torch
from PIL import Image
from sklearn.metrics import classification_report, confusion_matrix
from torch import nn
from torch.utils.data import DataLoader, Dataset

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.classifier import IMAGE_SIZE, _transform, build_model  # noqa: E402
from torchvision import transforms  # noqa: E402

MANIFEST_PATH = ROOT / "data" / "food_freshness_manifest.csv"
MODEL_OUT_PATH = ROOT / "models" / "freshness_classifier.pt"
RESULTS_DIR = ROOT / "results"
LABELS = ["fresh", "spoiled"]
LABEL_TO_IDX = {label: i for i, label in enumerate(LABELS)}
EPOCHS = 10
BATCH_SIZE = 16
LEARNING_RATE = 1e-3

_train_transform = transforms.Compose(
    [
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(10),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


class ManifestDataset(Dataset):
    def __init__(self, rows: list[dict], transform):
        self.rows = rows
        self.transform = transform

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, idx):
        row = self.rows[idx]
        image = Image.open(ROOT / row["path"]).convert("RGB")
        return self.transform(image), LABEL_TO_IDX[row["label"]]


def load_manifest() -> dict[str, list[dict]]:
    rows_by_split: dict[str, list[dict]] = {"train": [], "val": [], "test": []}
    with open(MANIFEST_PATH) as f:
        for row in csv.DictReader(f):
            rows_by_split[row["split"]].append(row)
    return rows_by_split


def run_epoch(model, loader, optimizer, criterion, train: bool) -> tuple[float, float]:
    model.train(train)
    total_loss, correct, total = 0.0, 0, 0
    for images, targets in loader:
        if train:
            optimizer.zero_grad()
        with torch.set_grad_enabled(train):
            logits = model(images)
            loss = criterion(logits, targets)
            if train:
                loss.backward()
                optimizer.step()
        total_loss += loss.item() * images.size(0)
        correct += (logits.argmax(dim=1) == targets).sum().item()
        total += images.size(0)
    return total_loss / total, correct / total


def evaluate(model, loader) -> tuple[list[int], list[int]]:
    model.eval()
    all_preds, all_targets = [], []
    with torch.no_grad():
        for images, targets in loader:
            preds = model(images).argmax(dim=1)
            all_preds.extend(preds.tolist())
            all_targets.extend(targets.tolist())
    return all_preds, all_targets


def main():
    rows_by_split = load_manifest()
    train_ds = ManifestDataset(rows_by_split["train"], _train_transform)
    val_ds = ManifestDataset(rows_by_split["val"], _transform)
    test_ds = ManifestDataset(rows_by_split["test"], _transform)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE)

    label_counts = [sum(1 for r in rows_by_split["train"] if r["label"] == label) for label in LABELS]
    class_weights = torch.tensor([1.0 / c for c in label_counts])
    class_weights = class_weights / class_weights.sum() * len(LABELS)

    model = build_model(num_classes=len(LABELS), freeze_backbone=True)
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = torch.optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)

    best_val_acc = 0.0
    history = []
    start = time.time()
    for epoch in range(1, EPOCHS + 1):
        train_loss, train_acc = run_epoch(model, train_loader, optimizer, criterion, train=True)
        val_preds, val_targets = evaluate(model, val_loader)
        val_acc = sum(p == t for p, t in zip(val_preds, val_targets)) / len(val_targets)
        history.append({"epoch": epoch, "train_loss": train_loss, "train_acc": train_acc, "val_acc": val_acc})
        print(f"epoch {epoch}: train_loss={train_loss:.4f} train_acc={train_acc:.3f} val_acc={val_acc:.3f}")
        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            MODEL_OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            torch.save({"state_dict": model.state_dict(), "labels": LABELS}, MODEL_OUT_PATH)

    elapsed = time.time() - start
    print(f"training took {elapsed:.1f}s, best val_acc={best_val_acc:.3f}")

    checkpoint = torch.load(MODEL_OUT_PATH, map_location="cpu", weights_only=False)
    model.load_state_dict(checkpoint["state_dict"])
    test_preds, test_targets = evaluate(model, test_loader)

    report = classification_report(test_targets, test_preds, target_names=LABELS, output_dict=True)
    matrix = confusion_matrix(test_targets, test_preds).tolist()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    metrics = {
        "labels": LABELS,
        "test_accuracy": report["accuracy"],
        "per_class": {label: report[label] for label in LABELS},
        "confusion_matrix": matrix,
        "confusion_matrix_order": LABELS,
        "train_history": history,
        "train_images": len(train_ds),
        "val_images": len(val_ds),
        "test_images": len(test_ds),
        "epochs": EPOCHS,
        "training_seconds": elapsed,
    }
    with open(RESULTS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics["per_class"], indent=2))
    print(f"test accuracy: {metrics['test_accuracy']:.3f}")
    print(f"confusion matrix ({LABELS}): {matrix}")


if __name__ == "__main__":
    main()

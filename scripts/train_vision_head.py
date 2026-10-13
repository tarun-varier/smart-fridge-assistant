#!/usr/bin/env python
"""Phase 2 step 2: train the MLP head on cached features (issue #11).

AdamW, lr 1e-3, weight decay 1e-4, batch 64, unweighted cross-entropy,
up to 40 epochs, early stopping on val accuracy (patience 5), best-epoch
checkpointing.
"""

import copy
import sys
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vision.model import VisionHead  # noqa: E402

FEATURES_DIR = ROOT / "data" / "features"
CHECKPOINT_PATH = ROOT / "models" / "vision_head_best.pt"

BATCH_SIZE = 64
MAX_EPOCHS = 40
PATIENCE = 5
LR = 1e-3
WEIGHT_DECAY = 1e-4


def load_split(split: str) -> TensorDataset:
    data = torch.load(FEATURES_DIR / f"{split}.pt")
    return TensorDataset(data["features"], data["labels"])


def evaluate(model: nn.Module, loader: DataLoader) -> float:
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for features, labels in loader:
            preds = model(features).argmax(dim=1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    return correct / total


def main() -> None:
    train_loader = DataLoader(load_split("train"), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(load_split("val"), batch_size=BATCH_SIZE, shuffle=False)

    model = VisionHead()
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0.0
    best_state = None
    epochs_without_improvement = 0

    for epoch in range(1, MAX_EPOCHS + 1):
        model.train()
        for features, labels in train_loader:
            optimizer.zero_grad()
            loss = criterion(model(features), labels)
            loss.backward()
            optimizer.step()

        val_acc = evaluate(model, val_loader)
        print(f"epoch {epoch:02d}  val_acc={val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_state = copy.deepcopy(model.state_dict())
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= PATIENCE:
                print(f"early stopping at epoch {epoch} (best val_acc={best_val_acc:.4f})")
                break

    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": best_state, "val_acc": best_val_acc}, CHECKPOINT_PATH)
    print(f"best val_acc={best_val_acc:.4f} -> {CHECKPOINT_PATH}")


if __name__ == "__main__":
    main()

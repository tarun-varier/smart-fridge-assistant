#!/usr/bin/env python
"""Phase 5: evaluation (issue #13: Evaluation metrics & report structure).

Vision Pipeline: accuracy, macro per-class precision/recall/F1, 6x6
confusion matrix, and a derived binary fresh/rotten roll-up, against the
held-out `data/raw/dataset/test/` split.

Receipt Pipeline: runs the hand-labeled real-receipt set (see
`data/real_receipts/labels.csv`, format below) through the live upload
path (`receipt.pipeline.run_receipt_pipeline`) and scores Category-match
correctness and exact-date-match, per the issue #13 resolution. Skipped
with a note if that set hasn't been collected yet.

`data/real_receipts/labels.csv` columns (one row per physical line item,
in the order it appears on the receipt):
    image,line_index,true_category,true_date
  - image: filename inside data/real_receipts/images/
  - line_index: 0-based order of this line item on the receipt
  - true_category: apple | banana | orange | unrecognized category
  - true_date: ISO date (YYYY-MM-DD), repeated for every line of one
    receipt -- one purchase date per receipt (CONTEXT.md: Receipt Pipeline)

Extracted line items are matched to ground truth by position (line_index)
since Donut's extraction has no stable item identity to match on.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from PIL import Image
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from receipt.categories import UNRECOGNIZED  # noqa: E402
from receipt.pipeline import run_receipt_pipeline  # noqa: E402
from vision.dataset import CLASS_TO_IDX, CLASSES  # noqa: E402
from vision.features import ManifestImageDataset, build_frozen_resnet18, extract_features  # noqa: E402
from vision.model import VisionHead  # noqa: E402

TEST_DIR = ROOT / "data" / "raw" / "dataset" / "test"
CHECKPOINT_PATH = ROOT / "models" / "vision_head_best.pt"
REAL_RECEIPTS_DIR = ROOT / "data" / "real_receipts"
LABELS_CSV = REAL_RECEIPTS_DIR / "labels.csv"
IMAGES_DIR = REAL_RECEIPTS_DIR / "images"

FIGURES_DIR = ROOT / "docs" / "figures"
RESULTS_MD = ROOT / "docs" / "evaluation-results.md"


# ---------------------------------------------------------------------------
# Generic confusion-matrix / precision-recall-F1 helpers (no sklearn dep)
# ---------------------------------------------------------------------------


def confusion_matrix(labels: torch.Tensor, preds: torch.Tensor, num_classes: int) -> torch.Tensor:
    cm = torch.zeros((num_classes, num_classes), dtype=torch.int64)
    for true, pred in zip(labels.tolist(), preds.tolist()):
        cm[true, pred] += 1
    return cm


def per_class_precision_recall_f1(cm: torch.Tensor) -> list[dict]:
    num_classes = cm.shape[0]
    rows = []
    for c in range(num_classes):
        tp = cm[c, c].item()
        fp = cm[:, c].sum().item() - tp
        fn = cm[c, :].sum().item() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        rows.append({"precision": precision, "recall": recall, "f1": f1})
    return rows


def plot_confusion_matrix(cm: torch.Tensor, class_names: list[str], title: str, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(1.2 * len(class_names) + 2, 1.2 * len(class_names) + 2))
    im = ax.imshow(cm.numpy(), cmap="Blues")
    ax.set_xticks(range(len(class_names)))
    ax.set_yticks(range(len(class_names)))
    ax.set_xticklabels(class_names, rotation=45, ha="right")
    ax.set_yticklabels(class_names)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    max_val = cm.max().item() or 1
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            value = cm[i, j].item()
            color = "white" if value > max_val / 2 else "black"
            ax.text(j, i, str(value), ha="center", va="center", color=color)
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Vision Pipeline evaluation
# ---------------------------------------------------------------------------


def build_test_rows() -> list[dict]:
    rows = []
    for cls in CLASSES:
        cls_dir = TEST_DIR / cls
        for path in sorted(cls_dir.iterdir()):
            if path.is_file():
                rows.append({"path": str(path), "label": cls})
    return rows


def load_vision_head() -> torch.nn.Module:
    head = VisionHead()
    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu")
    head.load_state_dict(checkpoint["state_dict"])
    head.eval()
    return head


def evaluate_vision() -> dict:
    rows = build_test_rows()
    dataset = ManifestImageDataset(rows, CLASS_TO_IDX)
    loader = DataLoader(dataset, batch_size=64, shuffle=False, num_workers=0)

    backbone = build_frozen_resnet18()
    features, labels = extract_features(backbone, loader)

    head = load_vision_head()
    with torch.no_grad():
        preds = head(features).argmax(dim=1)

    accuracy = (preds == labels).float().mean().item()
    cm = confusion_matrix(labels, preds, len(CLASSES))
    per_class = per_class_precision_recall_f1(cm)
    macro_precision = sum(r["precision"] for r in per_class) / len(per_class)
    macro_recall = sum(r["recall"] for r in per_class) / len(per_class)
    macro_f1 = sum(r["f1"] for r in per_class) / len(per_class)

    plot_confusion_matrix(cm, CLASSES, "Vision Pipeline -- 6-class confusion matrix", FIGURES_DIR / "vision_confusion_matrix.png")

    # Binary fresh/rotten roll-up: collapse the 3 food types.
    is_rotten = torch.tensor([cls.startswith("rotten") for cls in CLASSES])
    binary_labels = is_rotten[labels].long()
    binary_preds = is_rotten[preds].long()
    binary_cm = confusion_matrix(binary_labels, binary_preds, 2)
    binary_accuracy = (binary_preds == binary_labels).float().mean().item()
    binary_metrics = per_class_precision_recall_f1(binary_cm)

    plot_confusion_matrix(
        binary_cm, ["fresh", "rotten"], "Vision Pipeline -- binary fresh/rotten roll-up", FIGURES_DIR / "vision_binary_confusion_matrix.png"
    )

    return {
        "n_test": len(rows),
        "accuracy": accuracy,
        "per_class": per_class,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "confusion_matrix": cm,
        "binary_accuracy": binary_accuracy,
        "binary_metrics": binary_metrics,
        "binary_confusion_matrix": binary_cm,
    }


# ---------------------------------------------------------------------------
# Receipt Pipeline evaluation
# ---------------------------------------------------------------------------


def load_receipt_labels() -> dict[str, list[dict]]:
    """Group hand-labeled ground truth rows by receipt image, in line order."""
    by_image: dict[str, list[dict]] = defaultdict(list)
    with LABELS_CSV.open() as f:
        for row in csv.DictReader(f):
            by_image[row["image"]].append(row)
    for rows in by_image.values():
        rows.sort(key=lambda r: int(r["line_index"]))
    return by_image


def evaluate_receipts() -> dict | None:
    if not LABELS_CSV.exists():
        return None
    by_image = load_receipt_labels()
    if not by_image:
        return None

    category_correct = 0
    category_total = 0
    false_unrecognized = 0  # true category is a real food, extracted as unrecognized
    real_category_total = 0

    date_exact = 0
    date_wrong = 0
    date_missing = 0
    date_total = 0

    for image_name, truth_rows in by_image.items():
        image = Image.open(IMAGES_DIR / image_name)
        extracted = run_receipt_pipeline(image)

        for truth, line in zip(truth_rows, extracted):
            category_total += 1
            if line.category == truth["true_category"]:
                category_correct += 1
            if truth["true_category"] != UNRECOGNIZED:
                real_category_total += 1
                if line.category == UNRECOGNIZED:
                    false_unrecognized += 1
        # Extracted lines beyond the ground-truth count, or missing ones, are
        # simply not scored on this axis (positional zip already stops short).

        true_date = truth_rows[0]["true_date"]
        extracted_date = extracted[0].purchase_date if extracted else None
        date_total += 1
        if extracted_date is None:
            date_missing += 1
        elif extracted_date.isoformat() == true_date:
            date_exact += 1
        else:
            date_wrong += 1

    return {
        "n_receipts": len(by_image),
        "category_correct": category_correct,
        "category_total": category_total,
        "category_accuracy": category_correct / category_total if category_total else 0.0,
        "false_unrecognized": false_unrecognized,
        "real_category_total": real_category_total,
        "false_unrecognized_rate": false_unrecognized / real_category_total if real_category_total else 0.0,
        "date_exact": date_exact,
        "date_wrong": date_wrong,
        "date_missing": date_missing,
        "date_total": date_total,
        "date_exact_rate": date_exact / date_total if date_total else 0.0,
        "date_wrong_rate": date_wrong / date_total if date_total else 0.0,
        "date_missing_rate": date_missing / date_total if date_total else 0.0,
    }


# ---------------------------------------------------------------------------
# Results write-up
# ---------------------------------------------------------------------------


def render_vision_section(v: dict) -> str:
    lines = [
        "## Vision Pipeline",
        "",
        f"Evaluated against the held-out `data/raw/dataset/test/` split ({v['n_test']} images).",
        "",
        f"- **Overall accuracy:** {v['accuracy']:.4f}",
        f"- **Macro precision:** {v['macro_precision']:.4f}",
        f"- **Macro recall:** {v['macro_recall']:.4f}",
        f"- **Macro F1:** {v['macro_f1']:.4f}",
        "",
        "### Per-class",
        "",
        "| Class | Precision | Recall | F1 |",
        "| --- | --- | --- | --- |",
    ]
    for cls, metrics in zip(CLASSES, v["per_class"]):
        lines.append(f"| {cls} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1']:.4f} |")

    lines += [
        "",
        "### Confusion matrix",
        "",
        "![Vision 6-class confusion matrix](figures/vision_confusion_matrix.png)",
        "",
        "### Binary fresh/rotten roll-up",
        "",
        f"- **Accuracy:** {v['binary_accuracy']:.4f}",
        "",
        "| Class | Precision | Recall | F1 |",
        "| --- | --- | --- | --- |",
    ]
    for cls, metrics in zip(["fresh", "rotten"], v["binary_metrics"]):
        lines.append(f"| {cls} | {metrics['precision']:.4f} | {metrics['recall']:.4f} | {metrics['f1']:.4f} |")
    lines += [
        "",
        "![Vision binary fresh/rotten confusion matrix](figures/vision_binary_confusion_matrix.png)",
        "",
    ]
    return "\n".join(lines)


def render_receipt_section(r: dict | None) -> str:
    if r is None:
        return "\n".join(
            [
                "## Receipt Pipeline",
                "",
                "**Pending.** No hand-labeled real-receipt set found at "
                f"`{LABELS_CSV.relative_to(ROOT)}` yet (Phase 1's ~15-20 "
                "real-receipt collection, per issue #13, hasn't landed). "
                "Add hand-photographed receipts to "
                f"`{IMAGES_DIR.relative_to(ROOT)}/` and ground truth rows to "
                f"`{LABELS_CSV.relative_to(ROOT)}` (see `scripts/evaluate.py`'s "
                "module docstring for the format), then rerun "
                "`python scripts/evaluate.py`.",
                "",
            ]
        )

    lines = [
        "## Receipt Pipeline",
        "",
        f"Evaluated against {r['n_receipts']} hand-photographed, hand-labeled real receipts "
        f"({r['category_total']} line items), run through the live Streamlit upload path.",
        "",
        "### Category-match correctness",
        "",
        f"- **Accuracy:** {r['category_accuracy']:.4f} ({r['category_correct']}/{r['category_total']}) "
        "-- a correctly-flagged `unrecognized category` line counts as correct.",
        f"- **False unrecognized-flag rate:** {r['false_unrecognized_rate']:.4f} "
        f"({r['false_unrecognized']}/{r['real_category_total']}) -- real apple/banana/orange lines "
        "wrongly flagged `unrecognized category`.",
        "",
        "### Date extraction (exact calendar-date match)",
        "",
        f"- **Exact match:** {r['date_exact_rate']:.4f} ({r['date_exact']}/{r['date_total']})",
        f"- **Wrong date:** {r['date_wrong_rate']:.4f} ({r['date_wrong']}/{r['date_total']})",
        f"- **No date found:** {r['date_missing_rate']:.4f} ({r['date_missing']}/{r['date_total']})",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    print("Evaluating Vision Pipeline against held-out test/ ...")
    vision_results = evaluate_vision()
    print(f"  accuracy={vision_results['accuracy']:.4f} macro_f1={vision_results['macro_f1']:.4f}")

    print("Evaluating Receipt Pipeline against hand-labeled real receipts ...")
    receipt_results = evaluate_receipts()
    if receipt_results is None:
        print(f"  skipped: no labels found at {LABELS_CSV}")
    else:
        print(f"  category_accuracy={receipt_results['category_accuracy']:.4f} "
              f"date_exact_rate={receipt_results['date_exact_rate']:.4f}")

    sections = [
        "# Evaluation results",
        "",
        "Generated by `scripts/evaluate.py` (issue #13: Evaluation metrics & report structure). "
        "`docs/report.md` embeds/links these rather than restating the numbers.",
        "",
        render_vision_section(vision_results),
        render_receipt_section(receipt_results),
    ]
    RESULTS_MD.write_text("\n".join(sections))
    print(f"-> {RESULTS_MD}")


if __name__ == "__main__":
    main()

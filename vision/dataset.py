"""Category vocabulary and train/val split manifest for the Vision Pipeline.

Classes match the sriramr/fruits-fresh-and-rotten-for-classification folder
names exactly (see docs/implementation-task-breakdown.md Phase 1/2 and
.scratch/smart-fridge/issues/01-vision-dataset-research.md), so no relabeling
step is needed.
"""

import csv
import random
from pathlib import Path

CLASSES = [
    "freshapples",
    "freshbanana",
    "freshoranges",
    "rottenapples",
    "rottenbanana",
    "rottenoranges",
]
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASSES)}

# Per issue #5 (Vision Pipeline Architecture): 85/15 stratified split carved
# out of train/; the shipped test/ folder stays untouched for Phase 5 eval.
VAL_FRACTION = 0.15
SPLIT_SEED = 42


def build_split_manifest(train_dir: Path) -> list[dict]:
    """Stratified 85/15 split: shuffle each class's files independently."""
    rows = []
    for cls in CLASSES:
        cls_dir = train_dir / cls
        files = sorted(p for p in cls_dir.iterdir() if p.is_file())
        rng = random.Random(SPLIT_SEED)
        rng.shuffle(files)
        n_val = round(len(files) * VAL_FRACTION)
        for p in files[:n_val]:
            rows.append({"path": str(p), "label": cls, "split": "val"})
        for p in files[n_val:]:
            rows.append({"path": str(p), "label": cls, "split": "train"})
    return rows


def write_manifest(rows: list[dict], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "label", "split"])
        writer.writeheader()
        writer.writerows(rows)


def read_manifest(manifest_path: Path, split: str) -> list[dict]:
    with manifest_path.open() as f:
        return [row for row in csv.DictReader(f) if row["split"] == split]

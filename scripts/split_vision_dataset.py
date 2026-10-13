#!/usr/bin/env python
"""Phase 1: build the 85/15 train/val split manifest from data/raw/dataset/train.

The shipped test/ folder is never read here -- it stays held out for
Phase 5 evaluation (docs/implementation-task-breakdown.md).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vision.dataset import build_split_manifest, write_manifest  # noqa: E402

TRAIN_DIR = ROOT / "data" / "raw" / "dataset" / "train"
MANIFEST_PATH = ROOT / "data" / "vision_splits.csv"


def main() -> None:
    rows = build_split_manifest(TRAIN_DIR)
    write_manifest(rows, MANIFEST_PATH)
    n_train = sum(1 for r in rows if r["split"] == "train")
    n_val = sum(1 for r in rows if r["split"] == "val")
    print(f"train={n_train} val={n_val} total={len(rows)} -> {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

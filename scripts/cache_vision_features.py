#!/usr/bin/env python
"""Phase 2 step 1: cache frozen-ResNet18 features for train/val (ADR 0001, "Plan A")."""

import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vision.dataset import CLASS_TO_IDX, read_manifest  # noqa: E402
from vision.features import ManifestImageDataset, build_frozen_resnet18, extract_features  # noqa: E402

MANIFEST_PATH = ROOT / "data" / "vision_splits.csv"
FEATURES_DIR = ROOT / "data" / "features"
BATCH_SIZE = 64


def cache_split(split: str, backbone: torch.nn.Module) -> None:
    rows = read_manifest(MANIFEST_PATH, split)
    dataset = ManifestImageDataset(rows, CLASS_TO_IDX)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    start = time.time()
    features, labels = extract_features(backbone, loader)
    elapsed = time.time() - start

    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = FEATURES_DIR / f"{split}.pt"
    torch.save({"features": features, "labels": labels}, out_path)
    print(f"{split}: {features.shape[0]} images, {features.shape[1]}-d features, "
          f"{elapsed:.1f}s -> {out_path}")


def main() -> None:
    backbone = build_frozen_resnet18()
    for split in ("train", "val"):
        cache_split(split, backbone)


if __name__ == "__main__":
    main()

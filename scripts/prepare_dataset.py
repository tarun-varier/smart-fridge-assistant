"""Turn the raw Kaggle fresh-vs-rotten-fruit-images download into a clean,
binary (fresh/spoiled) manifest with a stratified train/val/test split that
keeps near-duplicate photos out of both splits at once.

v2: a cross-model review caught a real bug in v1. v1 deduped by stripping the
file extension from the filename, assuming same-basename-different-extension
files were the same photo saved three ways. Direct pixel comparison disproves
that (mean abs diff 40-136 out of 255 between them — genuinely different
photos that happened to share a name prefix). Meanwhile the raw dataset has a
real, different duplication problem: many numbered variants
("apple_fresh_001.jpg (14).jpg", "... (41).jpg", ...) within the same folder
are pixel-near-identical (diff under 1/255) — the same photo saved multiple
times under different sequence numbers. Splitting those across train/test
leaks the test label. This version clusters by actual pixel similarity
(16x16 grayscale, mean abs diff < 10) and keeps each cluster in one split.

Run with the project venv: .venv/bin/python scripts/prepare_dataset.py
"""

import csv
import random
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "food_freshness" / "Fruit Freshness Dataset" / "Fruit Freshness Dataset"
MANIFEST_PATH = ROOT / "data" / "food_freshness_manifest.csv"

IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp", ".jfif"]
LABEL_MAP = {"Fresh": "fresh", "Rotten": "spoiled"}
SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}
SEED = 42
HASH_SIZE = 16
NEAR_DUP_THRESHOLD = 10.0  # mean abs diff on 0-255 scale; true dupes measured at 0-0.25, distinct photos at 40+


def perceptual_hash(path: Path) -> np.ndarray:
    image = Image.open(path).convert("L").resize((HASH_SIZE, HASH_SIZE))
    return np.asarray(image, dtype=np.float32).flatten()


def cluster_by_similarity(paths: list[Path]) -> list[list[Path]]:
    """Group paths whose downsampled grayscale content is near-identical."""
    hashes = np.stack([perceptual_hash(p) for p in paths])
    n = len(paths)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i, j):
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[ri] = rj

    for i in range(n):
        diffs = np.abs(hashes[i + 1 :] - hashes[i]).mean(axis=1) if i + 1 < n else np.array([])
        for offset, diff in enumerate(diffs):
            if diff < NEAR_DUP_THRESHOLD:
                union(i, i + 1 + offset)

    clusters: dict[int, list[Path]] = {}
    for idx, path in enumerate(paths):
        root = find(idx)
        clusters.setdefault(root, []).append(path)
    return list(clusters.values())


def assign_splits(count: int, rng: random.Random) -> list[str]:
    indices = list(range(count))
    rng.shuffle(indices)
    n_train = round(count * SPLIT_RATIOS["train"])
    n_val = round(count * SPLIT_RATIOS["val"])
    split_for_index = {}
    for i, idx in enumerate(indices):
        if i < n_train:
            split_for_index[idx] = "train"
        elif i < n_train + n_val:
            split_for_index[idx] = "val"
        else:
            split_for_index[idx] = "test"
    return [split_for_index[i] for i in range(count)]


def main():
    rng = random.Random(SEED)
    rows = []
    total_raw = 0
    total_clusters = 0

    for fruit_dir in sorted(RAW_DIR.iterdir()):
        if not fruit_dir.is_dir():
            continue
        for raw_label, label in LABEL_MAP.items():
            label_dir = fruit_dir / raw_label
            if not label_dir.is_dir():
                continue
            images = sorted(p for p in label_dir.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)
            total_raw += len(images)
            if not images:
                continue
            clusters = cluster_by_similarity(images)
            total_clusters += len(clusters)
            splits = assign_splits(len(clusters), rng)
            for cluster, split in zip(clusters, splits):
                for path in cluster:
                    rows.append(
                        {
                            "path": str(path.relative_to(ROOT)),
                            "fruit": fruit_dir.name,
                            "label": label,
                            "split": split,
                            "cluster_size": len(cluster),
                        }
                    )

    with open(MANIFEST_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "fruit", "label", "split", "cluster_size"])
        writer.writeheader()
        writer.writerows(rows)

    by_label = {}
    by_split = {}
    for row in rows:
        by_label[row["label"]] = by_label.get(row["label"], 0) + 1
        by_split[row["split"]] = by_split.get(row["split"], 0) + 1

    print(f"raw images: {total_raw}, clusters (unique photos): {total_clusters}")
    print(f"wrote {MANIFEST_PATH} ({len(rows)} images across {total_clusters} clusters)")
    print("by label:", by_label)
    print("by split (image count):", by_split)


if __name__ == "__main__":
    main()

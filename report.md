# Smart Fridge / Food Waste Reduction Assistant — Report

## Problem

Households throw away food because they forget what's in the fridge or can't tell whether an item is still good. This project builds a multimodal CV + NLP pipeline that scans a fridge photo for freshness and a grocery receipt for expiry, then surfaces what needs using up soon.

## Architecture

1. **Detection** — a pretrained YOLOv8n (COCO weights, not fine-tuned) locates candidate food items in a fridge photo and crops them.
2. **Freshness classification** — a MobileNetV2 backbone (frozen, ImageNet-pretrained) with a fine-tuned linear head, trained on a fresh-vs-rotten fruit dataset, labels each crop.
3. **Receipt OCR** — EasyOCR (pretrained, not fine-tuned) extracts text from a receipt photo.
4. **Parsing** — regex groups OCR boxes into rows, pulls item + price lines and the purchase date (`dateparser`, DMY order).
5. **Expiry estimation** — a curated shelf-life lookup table turns purchase date + item name into an estimated expiry date.
6. **App** — Streamlit ties it together: fridge scan, receipt scan, and a near-expiry recipe suggestion.

## Datasets

**Freshness classifier:** [Fruit Freshness Classification (Fresh vs Rotten)](https://www.kaggle.com/datasets/abdulrafeyyashir/fresh-vs-rotten-fruit-images) — Apple/Banana/Strawberry, Fresh/Rotten, ~40MB. Chosen over the brief's named "Food Freshness Dataset" (6.3GB) because it's small enough to fine-tune on CPU in a few minutes while still being a clean, well-labeled fresh/rotten binary task; this does narrow the demo to 3 fruit types rather than general fridge contents. The raw download (566 images) has heavy duplication — many images recur under different sequence numbers within the same folder, pixel-identical or nearly so. These are grouped into 343 unique-photo clusters (16×16 grayscale similarity, mean abs diff < 10/255) and each whole cluster — never an individual image — is assigned to train/val/test (70/15/15), so no photo (or near-identical near-twin of it) appears in more than one split. See "Real bugs found and fixed" below: an earlier version of this dedup step was wrong and leaked test images into train.

**Receipt OCR/parsing:** SROIE (Scanned Receipts OCR and Information Extraction) test-split images, used to measure purchase-date extraction accuracy against its ground truth. SROIE's ground truth only covers company/date/address/total — no per-item fields — so item-line extraction accuracy is measured separately on synthetic fixtures with known ground truth instead (see Results).

## Results

**Freshness classifier** (`results/metrics.json`, held-out test split, 84 images, no cluster shared with train — see dataset note above):

- Test accuracy: **92.9%**
- Fresh: precision 0.926, recall 0.962, F1 0.943 (52 images)
- Spoiled: precision 0.933, recall 0.875, F1 0.903 (32 images)
- Confusion matrix (rows = true, columns = predicted, order [fresh, spoiled]): `[[50, 2], [4, 28]]`
- Training: MobileNetV2 head only (backbone frozen), 10 epochs, class-weighted loss for the 66/34 fresh/spoiled imbalance, ~11 minutes on CPU.
- An earlier run reported 97.5% — inflated by a dedup bug that let near-duplicate photos leak into both train and test. See "Real bugs found and fixed."

**Receipt OCR + parsing** (SROIE test split, real photographed receipts):

- Tuning sample (`results/receipt_eval.json`, 20 receipts, used while developing the date-extraction fixes below): **16/20 (80%)**.
- Disjoint holdout sample (`results/receipt_eval_holdout.json`, 20 different receipts never seen during development): **18/20 (90%)**. Reported separately because an in-sample number after tuning fixes against it isn't a real generalization estimate; the holdout confirms the fixes generalize rather than overfitting to the tuning sample. The 2 holdout misses: one date printed as "05-JAN-2017" (a month-name format outside the numeric-date regex's scope — a known, documented limitation, not a bug), one single OCR-misread digit.
- Item-line extraction: no ground truth exists in SROIE for individual items, so item-match accuracy is measured on synthetic fixtures instead (`tests/fixtures/receipts/`, known ground truth): **6/6 items, 2/2 dates**.

## Real bugs found and fixed (via testing against ground truth, not self-report)

1. EasyOCR returns one box per detected word/phrase, not per printed line — item name and price landed in separate "lines," so the price-terminated-line regex matched nothing. Fixed by clustering boxes into rows by vertical overlap before parsing.
2. `dateparser` defaults to MM/DD; receipts here are DD/MM. Fixed by setting `DATE_ORDER: DMY`.
3. The date regex could match an OCR'd timestamp (`10.20.37 AM`) or a fuzzy-matched phone/GST-ID number as if it were a date, occasionally producing a year like 1937 or 1400. Fixed by rejecting AM/PM-adjacent matches and bounding accepted dates to [2000-01-01, today].
4. **Dataset leakage (caught by cross-model review, not self-caught).** The first version of `scripts/prepare_dataset.py` deduplicated by stripping the file extension from each filename, assuming same-basename-different-extension files (`photo (1).jpg`, `photo (1).png`, `photo (1).webp`) were the same photo saved three ways. Direct pixel comparison disproved that (mean abs diff 40-136 out of 255 — genuinely different photos). Worse, it missed the dataset's real duplication: many numbered variants within the same folder ARE pixel-near-identical (diff under 1/255) regardless of extension — the same photo saved multiple times under different sequence numbers. Splitting those across train/test leaked 45 of 79 test images into train, inflating test accuracy from an honest 92.9% to a reported 97.5%. Fixed by clustering on actual pixel similarity (16×16 grayscale, threshold 10/255) and keeping whole clusters within one split; post-fix, 1 of 84 test images has any near-match in train, and that one is a different label (fresh vs. spoiled), so it isn't a real leak.
5. The date-extraction fixes in item 3 were validated against the same 20-receipt sample used to report accuracy — an in-sample number, not evidence of generalization (also caught by cross-model review). Fixed by evaluating a second, disjoint 20-receipt sample never used during development; see Results.

## Limitations

- **Detection coverage.** COCO's food classes are sparse (apple, banana, orange, broccoli, carrot, sandwich, hot dog, pizza, donut, cake) — no milk, cheese, bread, or leafy greens. Most real fridge photos will fall back to whole-image classification rather than per-item cropping.
- **Freshness classifier scope.** Trained on 3 fruit types (apple, banana, strawberry) from a 40MB dataset, not the brief's named "Food Freshness Dataset" — a deliberate scope trade for CPU-feasible training time, not run past the person who wrote the brief before making it.
- **Shelf-life table.** Approximate public food-safety guidance, not personalized to actual storage temperature or condition at purchase.
- **No local GPU.** Classifier training ran on CPU with a frozen backbone — sufficient for this dataset's size, but not representative of what a from-scratch or larger fine-tune would need.
- **No live browser verification.** The app's import correctness and every underlying module were verified directly (headless server start, real images/receipts through the actual functions the app calls), but no one has clicked through the Streamlit UI itself in a browser yet — this session has no browser tool available. Worth doing before treating the app as demo-ready.
- **Date-format coverage.** The receipt date parser only recognizes numeric formats (`DD/MM/YYYY` and similar); month-name dates ("05-JAN-2017") aren't matched.

## How to run

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# place a Kaggle API token at ~/.kaggle/kaggle.json first
.venv/bin/python scripts/prepare_dataset.py
.venv/bin/python scripts/train_classifier.py
.venv/bin/streamlit run app/app.py
```

# Smart Fridge / Food Waste Reduction Assistant

A multimodal CV + NLP mini-project: detect food items in a fridge photo, classify freshness/spoilage, parse grocery receipts for purchase dates, and estimate expiry to cut household food waste.

## Pipeline

1. **Detection** — a pretrained YOLOv8n (COCO weights) locates candidate food items in a fridge photo and crops them.
2. **Freshness classification** — a transfer-learning CNN, fine-tuned on the Kaggle Food Freshness Dataset, labels each crop fresh or spoiled.
3. **Receipt OCR** — EasyOCR extracts text from a receipt photo; regex + `dateparser` pull item lines, prices, and the purchase date.
4. **Expiry estimation** — a curated shelf-life lookup table turns purchase date + item name into an estimated expiry date.
5. **App** — a Streamlit UI ties it together: fridge scan, receipt scan, a merged inventory sorted soonest-expiring-first, and a simple recipe suggestion for items expiring soon.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Place a Kaggle API token at `~/.kaggle/kaggle.json` (from kaggle.com/settings) before running `scripts/download_data.py`.

## Run

```bash
.venv/bin/streamlit run app/app.py
```

## Layout

- `data/` — downloaded datasets (gitignored).
- `notebooks/` — training/exploration notebooks.
- `src/` — pipeline modules (detection, classification, OCR, parsing, expiry).
- `app/` — Streamlit app.
- `models/` — exported model artifacts (gitignored).
- `results/` — metrics, plots, evaluation output.
- `tests/fixtures/` — sample images for the verification harness.
- `scripts/` — dataset download and verification scripts.

## Status

See `report.md` for datasets, architecture, measured metrics, and known limitations.

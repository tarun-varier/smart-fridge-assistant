# Smart Fridge / Food Waste Reduction Assistant

See [`docs/report.md`](docs/report.md) for the full writeup (problem, architecture, evaluation, demo walkthrough, limitations). This README only covers setup and how to run things.

## Setup

Requires Python 3.14, CPU only (no GPU), and a system install of Tesseract OCR (`tesseract` on `PATH` — version 5.5.3 was used here).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

(A `Pipfile` is also provided if you prefer `pipenv install`.)

Download the Kaggle dataset `sriramr/fruits-fresh-and-rotten-for-classification` and unpack it to `data/raw/dataset/` (expects `train/` and `test/` subfolders, one directory per class) before running any Vision Pipeline scripts below.

## Run the Streamlit demo

```bash
streamlit run app.py
```

Upload a receipt photo, confirm/edit the purchase date, add it to the fridge, then use "Confirm with camera" on any alert to take or upload a photo for the Vision Pipeline to check. Requires `models/vision_head_best.pt` to exist — see below if it's missing.

## Reproduce the Vision Pipeline from scratch

```bash
python scripts/split_vision_dataset.py      # 85/15 train/val manifest from data/raw/dataset/train
python scripts/cache_vision_features.py     # cache frozen-ResNet18 features -> data/features/
python scripts/train_vision_head.py         # train the MLP head -> models/vision_head_best.pt
```

## Run the evaluation suite

```bash
python scripts/evaluate.py
```

Writes `docs/evaluation-results.md` and the confusion-matrix figures in `docs/figures/`. The Vision Pipeline section always runs (against `data/raw/dataset/test/`). The Receipt Pipeline section runs only once `data/real_receipts/labels.csv` and `data/real_receipts/images/` exist — see the module docstring in `scripts/evaluate.py` for the label format — and otherwise writes a pending note.

## Repo layout

- `app.py` — the Streamlit demo.
- `vision/`, `receipt/`, `fridge/` — the two pipelines and the shared Food Item state.
- `scripts/` — one-shot build/eval scripts (dataset split, feature caching, training, evaluation).
- `docs/` — report, evaluation results, ADRs, and research notes referenced from the report rather than restated here.

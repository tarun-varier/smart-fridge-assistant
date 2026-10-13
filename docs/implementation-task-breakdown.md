# Implementation task breakdown

Synthesizes every locked decision (issues #2–#13 on the wayfinder map) into an ordered, deadline-mapped checklist. Written 2026-10-07, 8 days out from the **Oct 15, 2026** deadline. Not a wayfinder ticket — nothing here is undecided; this is execution sequencing over decisions already made.

## Critical-path risks (start these first, in parallel with everything else)

- **Donut CPU inference speed is unverified** (flagged in [Receipt dataset & OCR research](https://github.com/tarun-varier/smart-fridge/issues/3)). Run a smoke test — one forward pass of `donut-base-finetuned-cord-v2` on a sample receipt image — on day 1, before committing real build time to the Receipt Pipeline. If it's too slow for an interactive Streamlit demo, that's a fact worth having by day 1, not day 4.
- **Real receipt collection for evaluation** (~15–20 hand-photographed receipts, per [Evaluation metrics & report structure](https://github.com/tarun-varier/smart-fridge/issues/13)) has a long lead time — it needs physical receipts and hand-labeling. Start collecting day 1 so the set is ready when Receipt Pipeline evaluation runs.

## Phase 1 — Setup & data (Oct 7–8)

- [x] Dev environment (`.venv`, pinned `requirements.txt`) — done, [issue #10](https://github.com/tarun-varier/smart-fridge/issues/10).
- [ ] Donut CPU speed smoke test (see risk above).
- [ ] Start collecting + hand-labeling the ~15–20 real receipts for Receipt Pipeline evaluation (ground-truth Category + date per line).
- [x] Download the Vision dataset (Kaggle `sriramr/fruits-fresh-and-rotten-for-classification`, [issue #2](https://github.com/tarun-varier/smart-fridge/issues/2)); split `train/` 85/15 into train/val, hold `test/` out untouched.
- [x] Implement the Shelf-Life Table lookup: hardcode fridge-days per Category from `docs/shelf-life-table.md` — collapse each range to one point value (e.g. apple fridge 28–42d, banana 3d once ripe, orange 10–21d) and record the chosen number inline as a comment, since the research ticket left the final collapse to implementation. (`fridge/shelf_life.py`.)

## Phase 2 — Vision Pipeline (Oct 8–9)

Per [Vision Pipeline Architecture](https://github.com/tarun-varier/smart-fridge/issues/5) and [Vision head hyperparameters](https://github.com/tarun-varier/smart-fridge/issues/11):

- [x] Cache frozen ResNet18 (ImageNet weights) features at 224×224 for train/val images, forward-only, no augmentation.
- [x] Train the MLP head (512→256→6, ReLU, dropout 0.3) on cached features: AdamW, LR 1e-3, weight decay 1e-4, batch size 64, plain unweighted cross-entropy, up to 40 epochs, early stopping on validation accuracy (patience 5), best-epoch checkpointing.
- [ ] Stretch, only if ahead of schedule: partial fine-tune of the last ResNet block ("Plan B").

## Phase 3 — Receipt Pipeline (Oct 9–10)

Per [Receipt Pipeline Architecture](https://github.com/tarun-varier/smart-fridge/issues/6) and [Category vocabulary & matching](https://github.com/tarun-varier/smart-fridge/issues/4):

- [x] Wire the two independent passes: `donut-base-finetuned-cord-v2` zero-shot for line-item extraction; Tesseract raw OCR + regex/`dateutil` for one receipt-level purchase date, broadcast to all line items. (`receipt/donut_extraction.py`, `receipt/date_extraction.py`, `receipt/pipeline.py`.)
- [x] Implement Category matching: normalize + `rapidfuzz` fuzzy match each extracted line against `{apple, banana, orange}` names/synonyms; flag no/ambiguous match as `unrecognized category`. (`receipt/categories.py`.)
- [x] No preprocessing step (deskew/binarization) — out of scope for v1 per the ADR. (Neither extraction pass runs one.)

## Phase 4 — Streamlit demo (Oct 10–11)

Per [Streamlit demo structure](https://github.com/tarun-varier/smart-fridge/issues/8):

- [x] Single page: receipt upload (editable/backdateable purchase date) → primary Alert list (date-based or visual-spoiled concerns, each with a "Confirm with camera" action via `camera_input` + file-upload fallback) → secondary Inventory table (non-alerting Categories) → collapsible Unrecognized-items section. (`app.py`.)
- [x] Food Item state: at most one per Category, replaced (not merged) on a new reading from either pipeline. (`fridge/state.py`.)
- [x] Vision Pipeline wired strictly reactive — only confirms/overrides an existing Date-Based signal, never runs independently. (`vision/infer.py`, called only from an alert's "Confirm with camera" action in `app.py`; `FridgeState.apply_vision` no-ops without an existing Food Item.)
- [x] Freshness conflict rule: Visual Freshness Signal wins over Date-Based on disagreement. (`fridge/freshness.py::resolve_freshness`.)

## Phase 5 — Evaluation (Oct 11–12)

Per [Evaluation metrics & report structure](https://github.com/tarun-varier/smart-fridge/issues/13):

- [x] `scripts/evaluate.py` — Vision Pipeline: accuracy, macro per-class precision/recall/F1, 6×6 confusion matrix, binary fresh/rotten roll-up, against held-out `test/`. Run: accuracy 0.9959, macro F1 0.9959.
- [ ] `scripts/evaluate.py` — Receipt Pipeline: scoring logic implemented and unit-verified (Category-match correctness, with a correctly-flagged `unrecognized category` counting as correct; exact-date-match with wrong-date/no-date tracked as separate sub-rates) but **blocked on the Phase 1 real-receipt collection task, still unstarted** — the script reads `data/real_receipts/labels.csv` (format documented in the script's docstring) and no-ops with a note in `docs/evaluation-results.md` until that set exists. Collect + hand-label the receipts, then rerun `python scripts/evaluate.py`.
- [x] Write figures to `docs/figures/` (`vision_confusion_matrix.png`, `vision_binary_confusion_matrix.png`), results table to `docs/evaluation-results.md` — Receipt Pipeline section will populate once its data lands.

## Phase 6 — Report & submission (Oct 12–14)

- [x] `docs/report.md` (plain Markdown): Problem & Motivation, Architecture, Dataset & Training, Evaluation Results, Demo Walkthrough, Limitations & Stretch Goals — embeds/links the eval figures and table rather than duplicating numbers.
- [x] README with setup instructions: `.venv`, `pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu`, how to run the Streamlit demo, how to run `scripts/evaluate.py`.
- [x] Rationale docs already in place (`docs/adr/0001-*.md`, `docs/adr/0002-*.md`, `docs/shelf-life-table.md`, `docs/receipt-finetuning-dataset-research.md`) — link from the report, don't restate.

## Phase 7 — Verification & buffer (Oct 14–15)

- [ ] Live call walkthrough with both teammates (per the map's Notes — no separate written sign-off artifact).
- [ ] Buffer for slippage; stretch items (YOLOv8 multi-item detection, recipe suggestions, mobile app, Donut fine-tuning, OCR preprocessing) only if genuinely ahead of schedule — all already deferred by their respective ADRs/tickets.
- [ ] Submit: report + repo + live Streamlit demo.

## Notes on sequencing

- Phases 2 and 3 (Vision, Receipt) are independent of each other and can overlap once Phase 1's setup is done.
- Phase 4 (Streamlit) depends on both Phase 2 and Phase 3 producing working, callable pipelines, plus the Shelf-Life Table from Phase 1.
- Phase 5 (Evaluation) depends on Phase 2–4 all being functional, and on the hand-labeled receipt set started in Phase 1.

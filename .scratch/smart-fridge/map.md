# Smart Fridge / Food Waste Reduction Assistant — Map

> **Superseded 2026-10-07.** This map and its tickets were migrated to GitHub issues (see the GitHub migration ticket below). The canonical map is now [tarun-varier/smart-fridge#1](https://github.com/tarun-varier/smart-fridge/issues/1); this file is left as a historical snapshot.

## Destination

A locked project spec for the Smart Fridge / Food Waste Reduction Assistant DL mini-project: architecture and dataset/model choices for the Vision Pipeline and Receipt Pipeline, the Food Item unification/matching design, and a task breakdown ready to implement toward the Oct 15, 2026 deadline. This map produces the plan only — implementation happens afterward in separate sessions (mostly solo, via Claude Code).

## Notes

- Domain vocabulary: see `CONTEXT.md` at repo root (Food Item, Category, Vision Pipeline, Receipt Pipeline, Visual/Date-Based Freshness Signal).
- Course context: DL mini-project, no rubric provided, deadline **Oct 15, 2026**. Team of 3 — Tarun (mail@techsigma.in) implements ~solo via Claude Code, two teammates review/verify locally over a call.
- Environment: CPU-only, no GPU, PyTorch not yet installed, 15GB RAM, Python 3.14.7. Transfer learning / fine-tuning pretrained backbones throughout — not from-scratch training (confirmed acceptable for grading).
- Scope, must-have: Vision Pipeline (fresh/spoiled classification on a single photo/crop), Receipt Pipeline (OCR extracting Category + purchase date), matching receipt text into the Vision Pipeline's fixed Category vocabulary (Food Item unification — chosen despite being extra scope), a local Streamlit demo with Shelf-Life-Table-based expiry alerts. Visual Freshness Signal wins over Date-Based Freshness Signal on conflict.
- Scope, stretch (cut first if short on time): YOLOv8 multi-item detection in a single fridge photo, recipe suggestions, mobile app instead of Streamlit.
- Out of scope: see below.
- Deployment: runs locally with README setup instructions; teammates verify over a call — no hosting/deployment infra in scope.
- Tracker: local-markdown (this file and its `issues/`) for now — GitHub was network-unreachable at charting time (2026-09-29). Migrate to a GitHub repo + issues once connectivity returns (see the github-migration ticket).
- Call the Skill tool for "grilling" and "domain-modeling" (updating `CONTEXT.md` inline) when resolving grilling-type tickets.

## Decisions so far

- [Vision dataset research](issues/01-vision-dataset-research.md): Use Kaggle `sriramr/fruits-fresh-and-rotten-for-classification` — 6 classes (fresh/rotten × apples/banana/oranges), ~13.6k images, smallest/most battle-tested fit for CPU-only training. `muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten` (28 classes) noted as a stretch extension.
- [Receipt dataset & OCR research](issues/02-receipt-dataset-ocr-research.md): Use CORD (CC BY 4.0) + official `donut-base-finetuned-cord-v2` for line-item extraction, plus Tesseract raw OCR + regex/`dateutil` for purchase date (CORD's schema has no date field; SROIE has date but no line items and an unverified license). Donut's CPU speed is unverified — flagged as a week-1 benchmarking task.
- [Category vocabulary & matching](issues/03-category-vocabulary-matching.md): Category vocabulary locked at `{apple, banana, orange}` (derived by stripping fresh/rotten off the Vision Pipeline's 6 classifier labels, not widened to the 28-class stretch dataset). Receipt lines matched via normalize + fuzzy-match against Category name/synonyms; no/ambiguous match flagged `unrecognized category` in the UI rather than dropped or bucketed.
- [Vision Pipeline Architecture](issues/04-vision-pipeline-architecture.md): ResNet18 @ 224×224, frozen backbone + cached-feature head training ("Plan A", required) with partial fine-tune of the last block as stretch ("Plan B"); 85/15 train/val split out of `train/`, `test/` held out; no augmentation for v1; a-few-hours training time ceiling. Rationale in `docs/adr/0001-vision-pipeline-backbone.md`.
- [Receipt Pipeline Architecture](issues/05-receipt-pipeline-architecture.md): `donut-base-finetuned-cord-v2` used zero-shot (no fine-tuning for v1) for line items, parallel independent Tesseract+regex pass for one receipt-level purchase date (broadcast to all line items, not per-item); no preprocessing; single-page-receipt-per-upload scope. Fine-tuning deferred to stretch, dataset research spun off into [Receipt fine-tuning dataset research](issues/11-receipt-finetuning-dataset-research.md). Rationale in `docs/adr/0002-receipt-pipeline-architecture.md`.
- [Shelf-Life Table](issues/06-shelf-life-table.md): USDA FoodKeeper-sourced days-until-spoilage for `{apple, banana, orange}` — apple 21d pantry/28–42d fridge, banana 3d fridge once ripe (no FoodKeeper pantry number, StillTasty fallback 2–5d), orange 10d pantry/10–21d fridge (via FoodKeeper's combined citrus-fruit entry). Data in `docs/shelf-life-table.md`.
- [Receipt fine-tuning dataset research](issues/11-receipt-finetuning-dataset-research.md): stretch-scope only. `albertobarnabo/synthetic-receipts-ocr` (Apache 2.0, 32k synthetic US+intl receipts) recommended as the fine-tuning corpus, supplemented by `docjay131/receipts-ocr-dataset` (MIT, 230 real photos, Gemini-labeled) as an eval set; `AdamCodd/donut-receipts-extract` checkpoint is an opportunistic fallback pending its manual access-gate; the Kaggle/`UniqueData` candidate ruled out (20-image teaser). Findings in `docs/receipt-finetuning-dataset-research.md`.
- [Streamlit demo structure](issues/07-streamlit-demo-structure.md): Receipt-first, vision-as-confirmation design (redirected mid-grill from an independent dual-upload design). Single page: receipt upload (with editable/backdateable purchase date) → primary Alert list (date-based or visual-spoiled concerns, each with a "Confirm with camera" action using `camera_input` + file-upload fallback) → secondary Inventory table (non-alerting Categories) → collapsible Unrecognized-items section. Vision Pipeline now strictly reactive (confirms/overrides an existing alert, never runs independently); Food Item can live on a Date-Based signal alone; at most one Food Item per Category. `CONTEXT.md`'s Food Item and Vision Pipeline entries updated inline.
- [GitHub migration](issues/08-github-migration.md): Repo created at [tarun-varier/smart-fridge](https://github.com/tarun-varier/smart-fridge) (private), local git history pushed, map + all 11 tickets migrated to GitHub issues with native sub-issue links and blocking dependencies. Old local ticket numbers → new issue numbers recorded on the ticket. The GitHub map issue is now canonical; this file is a historical snapshot.
- [Vision head hyperparameters](https://github.com/tarun-varier/smart-fridge/issues/11): MLP head (512→256→6, ReLU, dropout 0.3) on frozen cached ResNet18 features; AdamW, LR 1e-3, weight decay 1e-4; batch size 64; plain unweighted cross-entropy (mild ~1.6x class imbalance didn't warrant weighting); up to ~40 epochs with early stopping on validation accuracy (patience 5). Resolved on GitHub — see [issue #11](https://github.com/tarun-varier/smart-fridge/issues/11) for the live record; this file stays a historical snapshot.

## Not yet specified

- Recipe suggestion approach and mobile-app feasibility, if stretch scope is ever reached.

## Graduated to new tickets (see GitHub map)

- Evaluation metrics reporting format and report/submission structure graduated into [Evaluation metrics & report structure](https://github.com/tarun-varier/smart-fridge/issues/13) once both pipeline architectures and the vision head hyperparameters were locked.

## Out of scope

- Real barcode/inventory integration — beyond the original idea write-up's scope; no ticket was ever opened for it.

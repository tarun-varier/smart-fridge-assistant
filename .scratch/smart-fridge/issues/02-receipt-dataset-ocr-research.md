Type: research
Status: resolved

## Question

For the Receipt Pipeline (OCR + extraction of Category + purchase date from a grocery receipt), investigate:

- The CORD (Consolidated Receipt Dataset) and SROIE datasets: URL/download method, license (coursework-usable?), size, and exactly what fields they annotate (do they label line-item names and dates, or only totals/vendor/etc.?)
- What pretrained OCR/extraction options are realistic on CPU-only hardware within ~2.5 weeks: e.g. EasyOCR, Tesseract, or a pretrained document-understanding model (LayoutLMv3, Donut) fine-tuned on CORD/SROIE. Note approximate CPU inference speed and model size for each viable option.
- Whether extracting a purchase **date** from a receipt is something these datasets/models actually support out of the box, or whether that needs a separate regex/heuristic pass over the raw OCR text.

Write findings to a Markdown file (cite sources) and note where you saved it. Flag clearly which approach (dataset + OCR/extraction model combination) looks like the strongest fit given CPU-only inference and the deadline.

## Answer

**Recommendation: CORD + official `naver-clova-ix/donut-base-finetuned-cord-v2` for line-item extraction, plus Tesseract raw OCR text + a regex/`dateutil` pass for the purchase date.**

- **CORD** (github.com/clovaai/cord, HF `naver-clova-ix/cord-v2`) — CC BY 4.0, license confirmed directly from the GitHub README and HF dataset card (unambiguous, coursework-safe). 1,000 public receipt images, 800/100/100 train/dev/test. Schema: 30 classes including `menu.nm`/`menu.price`/`menu.cnt` — exactly the per-line-item fields this project needs. **No `date` entity anywhere in the schema.**
- **SROIE** (rrc.cvc.uab.es/?ch=13, arXiv:2103.10213) — 1,000 images (600/400 per the official paper; a commonly-mirrored redistribution reports 973/626-347 instead). Schema: only 4 receipt-level entities — `company`, `date`, `address`, `total` — **no per-line-item fields at all**. License could not be confirmed from the primary source (the official downloads page is login-gated); secondary mirrors disagree with each other (CC-BY-2.0 vs CC-BY-4.0), so it's flagged as unresolved rather than assumed safe.
- **CPU-friendly OCR/extraction options:** EasyOCR (Apache 2.0) and Tesseract (tessdata_fast ~4.1MB/language, official docs suggest ~1-3s/page on CPU) are both lightweight and CPU-native, though neither publishes a fixed throughput number. LayoutLMv3-base (CC BY-NC-SA 4.0, ~125M params) has no official CORD/SROIE checkpoint (only unofficial community fine-tunes) and isn't itself an OCR engine — it needs a separate OCR step feeding it words+boxes, adding pipeline complexity. Donut (MIT, ~143M params) has an **official, ready-to-run** CORD checkpoint (OCR-free end-to-end) but no official SROIE checkpoint; its only reported speed (~0.7s/image) was measured on a GPU, not CPU — no official CPU number exists, so this should be benchmarked on the target machine in week 1.
- **Date extraction:** CORD's schema has no date field, so any CORD-trained model (Donut or LayoutLMv3 alike) cannot output one natively. SROIE has a native `date` entity but no line-item fields and no official Donut checkpoint. Since no single dataset/model covers both line items and date, date extraction realistically needs a **separate regex/`dateutil` pass over raw OCR text** (from Tesseract) run alongside the CORD-based line-item model, rather than expecting it "for free" from either dataset.
- **Why this combination wins:** CORD's license is unambiguous where SROIE's is not; CORD covers the harder/more central requirement (line items) with a first-party, zero-shot-ready checkpoint, avoiding both the OCR-wiring overhead of LayoutLMv3 and the schedule risk of fine-tuning a model on SROIE from scratch within 2.5 weeks. Date is comparatively cheap and low-risk to bolt on separately via regex.

Full findings, citations, and caveats: `.scratch/smart-fridge/issues/02-research-findings.md` (this file also establishes `.scratch/smart-fridge/issues/` as the location for research notes, since the repo had no prior convention).

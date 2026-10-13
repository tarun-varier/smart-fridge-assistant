# Receipt Dataset & OCR/Extraction Research

This repo has no prior research-notes convention, so this file establishes a new location for
research findings at `.scratch/smart-fridge/issues/`. It documents the Receipt Pipeline
component of the Smart Fridge / Food Waste Reduction Assistant mini-project: OCR + extraction
of line-item names and purchase date from a grocery receipt photo, on a CPU-only inference
machine, with a hard deadline of Oct 15, 2026.

All claims below are followed by an inline citation to the primary source they came from
(official GitHub repo, official docs, Hugging Face model/dataset card, or the original paper).
Where a primary source could not be reached directly due to tooling limits (noted explicitly),
the claim is flagged as secondary/unverified rather than stated as fact.

---

## CORD dataset

**What it is.** CORD = "**CO**nsolidated **R**eceipt **D**ataset for post-OCR parsing," released
by NAVER CLOVA AI Research. Official GitHub repo:
https://github.com/clovaai/cord ("CORD: A Consolidated Receipt Dataset for Post-OCR Parsing").
Original paper: Park et al., *CORD: A Consolidated Receipt Dataset for Post-OCR Parsing*
(NeurIPS 2019 Document Intelligence Workshop), OpenReview PDF:
https://openreview.net/pdf?id=SJl3z659UH.

**Download.** Official Hugging Face dataset hub pages:
- https://huggingface.co/datasets/naver-clova-ix/cord-v1
- https://huggingface.co/datasets/naver-clova-ix/cord-v2

A small original-format (v0) sample is linked from the GitHub repo via Google Drive
(github.com/clovaai/cord README). Confirmed via direct fetch of
`raw.githubusercontent.com/clovaai/cord/master/README.md`.

**License.** **Creative Commons Attribution 4.0 International (CC BY 4.0)** — confirmed
directly from the GitHub README (raw fetch) and from the `naver-clova-ix/cord-v2` Hugging Face
dataset card (https://huggingface.co/datasets/naver-clova-ix/cord-v2). CC BY 4.0 permits
academic/coursework/non-commercial *and* commercial use, with attribution required — this is
unambiguously fine for a college mini-project.

**Size.** Publicly released: **1,000 Indonesian receipt images**, split **800 train / 100 dev
(validation) / 100 test** — confirmed both from the GitHub README and the
`naver-clova-ix/cord-v2` HF dataset card. Note: search-engine summaries of the underlying paper
(via a FiftyOne dataset-zoo card that mirrors CORD, https://huggingface.co/datasets/Voxel51/consolidated_receipt_dataset)
state the full underlying collection was **11,000 receipts**, of which only 1,000 were publicly
released due to personal-data privacy concerns. I could not confirm this 11,000 figure by directly
reading the OpenReview PDF (it served an anti-bot/login wall to the fetch tool), so treat it as
secondary-sourced context rather than a verified primary fact — the number that matters for the
project (1,000 public images, 800/100/100 split) *is* primary-confirmed.

**Annotation schema — critical finding.** CORD annotates **30 semantic classes grouped into 5
superclasses**: `menu`, `void_menu`, `subtotal`, `void_total`, `total` (confirmed via direct
GitHub README fetch, cross-checked against search-engine summaries of the same README/paper
content). Approximate breakdown:
- **menu** (~14 subclasses): `nm` (item name), `num`, `unitprice`, `cnt` (quantity),
  `discountprice`, `price`, `itemsubtotal`, `etc`, plus `sub_nm`/`sub_price`/`sub_cnt`/
  `sub_unitprice`/`sub_etc` for sub-items, `vatyn`
- **void_menu** (2): `nm`, `price`
- **subtotal** (6): `subtotal_price`, `discount_price`, `service_price`, `othersvc_price`,
  `tax_price`, `etc`
- **total** (8): `total_price`, `cashprice`, `changeprice`, `creditcardprice`, `emoneyprice`,
  `menutype_cnt`, `menuqty_cnt`, `total_etc`
- **void_total**: mirrors `total` structure for voided transactions

Plus lower-level OCR annotations: word/line bounding boxes + text, line grouping (`row_id`),
region-of-interest (`roi`), and an `is_key` flag.

**Line items: yes. Date: no.** CORD's `menu.nm` + `menu.price` (+ `menu.cnt`) fields are
*exactly* the per-line-item name/price/quantity annotations the project needs for food-item
extraction. **CORD's schema has no `date` entity anywhere in its 30 classes** — confirmed by
direct inspection of the class list above; there is no date superclass or subclass. This is
confirmed independently by two separate fetches of the same README/paper content that both
enumerate the full 30-class schema without a date field.

---

## SROIE dataset

**What it is.** SROIE = "**S**canned **R**eceipts **O**CR and **I**nformation **E**xtraction,"
the dataset behind the ICDAR 2019 Robust Reading Challenge. Official competition/task page
(Robust Reading Competition platform, run by the Computer Vision Center, UAB):
https://rrc.cvc.uab.es/?ch=13. Companion paper: Huang et al., *ICDAR2019 Competition on Scanned
Receipt OCR and Information Extraction*, arXiv:2103.10213 (https://arxiv.org/abs/2103.10213 /
https://arxiv.org/pdf/2103.10213), which is the official competition report.

**Tasks.** Three: **Task 1** — text localization; **Task 2** — OCR (word recognition, no
localization needed); **Task 3** — Key Information Extraction from receipts. (Confirmed via the
paper and via https://rrc.cvc.uab.es/?ch=13&com=tasks.)

**Download.** Through the official competition page https://rrc.cvc.uab.es/?ch=13 (downloads
section: `?ch=13&com=downloads`), which requires account registration/login on the RRC platform
before the dataset files and full terms become visible — I was only able to fetch the public,
unauthenticated overview/task pages of rrc.cvc.uab.es (repeated attempts to fetch the
login-gated downloads page returned only administrative competition-timeline text, no license
text or file links — noted explicitly rather than guessed at). Commonly used redistributions
exist on Hugging Face (e.g. https://huggingface.co/datasets/rth/sroie-2019-v2,
https://huggingface.co/datasets/darentang/sroie) and Kaggle (e.g.
https://www.kaggle.com/datasets/urbikn/sroie-datasetv2), all of which state they mirror the
original ICDAR/RRC release.

**License — unresolved from the primary source; flagging explicitly rather than guessing.**
The official ICDAR2019 SROIE paper (arXiv:2103.10213) contains **no explicit license, copyright,
or redistribution-terms statement** in its body — the closest it comes is "the new datasets used
in this competition will be made available after the event" and a note that sensitive fields
(name, address, contact number) are blurred for privacy. The rrc.cvc.uab.es downloads page (the
place license terms would actually be stated) sits behind a login the fetch tooling in this
session could not get past. Secondary mirrors disagree with each other: the
`rth/sroie-2019-v2` Hugging Face dataset card lists **CC-BY-2.0**; other summarized references
claim CC BY 4.0. **Recommendation for the project: do not assume a specific license — register
at https://rrc.cvc.uab.es/?ch=13 and read the Terms and Conditions on the actual downloads page
before relying on SROIE, or use CORD instead, whose CC BY 4.0 license is unambiguously confirmed
from the primary GitHub/HF sources above.**

**Size.** Per the official paper (arXiv:2103.10213): **1,000 total scanned receipt images**,
of which **600 were released to participants with annotations** during the competition and
**400 held out as the test set** (released closer to the submission deadline). Note: the
widely-redistributed post-competition dataset that most tutorials/mirrors use (e.g. the HF
`rth/sroie-2019-v2` card, and GitHub mirrors such as `zzzDavid/ICDAR-2019-SROIE`) reports **973
total images (626 train / 347 test)** — slightly smaller than the original 600/400 split, most
likely reflecting de-duplication or a few dropped/corrupted images in the commonly-circulated
copy. Both numbers are reported here since they come from different (but both traceable)
sources; the discrepancy itself is worth knowing about before citing a size in the project report.

**Annotation schema — critical finding.** Task 3 (Key Information Extraction) annotates exactly
**4 entity types per receipt: `company`, `date`, `address`, `total`** — this is stated by name in
the paper's discussion of the top-ranked team's regex approach ("company, cash, date, and
address" — arXiv:2103.10213) and stated explicitly as the 4-entity schema by downstream papers
that reuse SROIE (e.g. the entity list "company, date, address, and total" appears verbatim in
arXiv:2505.13535, a 2025 paper on visually-rich-document extraction that documents SROIE's
schema). **SROIE annotates only receipt-level/header fields — there is no per-line-item field at
all** (no item name, no item price, no quantity). This is the mirror-image gap of CORD: SROIE has
`date` natively but cannot give individual food-item names.

---

## CPU-friendly OCR/extraction options (EasyOCR, Tesseract, LayoutLMv3, Donut)

### EasyOCR
- Official repo: https://github.com/JaidedAI/EasyOCR. License: **Apache 2.0** (repo `LICENSE`
  file, confirmed via `setup.py` license field and GitHub issue #1422 discussing the license
  header).
- Architecture (from the README): **CRAFT** for text detection + a **CRNN** recognizer
  (ResNet/VGG backbone → LSTM → CTC decoding) — a general-purpose scene-text OCR engine, not
  a document-structure/field extractor.
- CPU support is first-class: `easyocr.Reader(['en'], gpu=False)` runs fully on CPU (README).
- **No fixed "seconds per image" benchmark number is published in the official README/docs.**
  The README/release notes (https://github.com/JaidedAI/EasyOCR/blob/master/releasenotes.md)
  state that a later release added "faster CPU inference speed by using dynamic input shape"
  (recognition throughput roughly doubling for text-heavy images) and introduced experimental
  "lite" recognition models that are "~7% of the file size" of the default models and "~6x
  faster" on CPU — but these are *relative* improvement claims, not absolute per-image timings.
  Stating this explicitly rather than inventing a number, per the task's instructions.
- Model size: not stated as a fixed number in the docs either; weights are downloaded
  automatically into `~/.EasyOCR/model` (README) and vary by language/detector/recognizer
  selection.

### Tesseract OCR
- Official docs: https://tesseract-ocr.github.io/tessdoc/tess4/4.0-Accuracy-and-Performance.html.
- Speed numbers reported are old (Tesseract 4.0-era), hardware-specific, single-page benchmarks,
  not a general throughput figure:
  - Google internal test, single Hindi page: LSTM engine 1.5s wall-time / 2.5s CPU-time vs.
    legacy Tesseract 3.04 3.0s wall-time / 2.8s CPU-time.
  - HP Z420 workstation, single Hindi page: "LSTM with OpenMP+AVX" 1.8s real / 3.8s user vs.
    base Tesseract 2.9s real / 2.6s user.
  - The same doc notes build configuration swings performance by 4x+ ("17 seconds with LSTM,
    4 seconds without, for the same image" on a release build vs. much slower debug builds).
  - Net takeaway from the official doc itself: expect **roughly 1–3 seconds per page on a single
    modern CPU core** for LSTM-mode OCR, but the docs explicitly caveat that this is highly
    hardware/build-dependent rather than a guaranteed number.
- Footprint (model/disk size): per the official `tessdata_fast` / `tessdata_best` repos and the
  tessdoc Data-Files page (https://github.com/tesseract-ocr/tessdata_fast,
  https://github.com/tesseract-ocr/tessdata_best,
  https://tesseract-ocr.github.io/tessdoc/Data-Files.html): **`tessdata_fast` models are ~4.1 MB
  per language** (integer-quantized, fastest, recommended default), the standard `tessdata` set
  is ~15 MB/language, and `tessdata_best` (most accurate, float models, slowest) is ~23
  MB/language. Tesseract itself is a lightweight native C++ binary with no GPU/deep-learning
  framework dependency, which is a real advantage for a CPU-only box with a tight deadline.

### LayoutLMv3
- Official HF model card: https://huggingface.co/microsoft/layoutlmv3-base. Paper: Huang et al.,
  *LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking* (ACM MM 2022).
- License: **CC BY-NC-SA 4.0** (Attribution-NonCommercial-ShareAlike 4.0 International) —
  stated on the model card. Non-commercial-only, but that's fine for a graded college project.
- Size: **~0.1B (≈125M) parameters** (base variant, per the HF model card).
- **No CPU inference speed/latency figure is given on the official model card** — stating this
  explicitly rather than guessing, as instructed.
- **No official Microsoft-published checkpoint fine-tuned on CORD or SROIE exists.** The
  `microsoft/layoutlmv3-base` card lists 300+ community fine-tuned derivatives but does not
  itself ship CORD/SROIE weights. Publicly available community fine-tunes found on the HF Hub:
  `nielsr/layoutlmv3-finetuned-cord` (F1 ≈ 0.9638 on CORD, by a Hugging Face staff member, widely
  used as the reference CORD checkpoint — https://huggingface.co/nielsr/layoutlmv3-finetuned-cord),
  and several SROIE community fine-tunes such as `Theivaprakasham/layoutlmv3-finetuned-sroie`
  and `mp-02/layoutlmv3-base-sroie`. These are **not official/first-party**, so quality and
  maintenance are not guaranteed — a real risk given a 2.5-week deadline.
- **Important pipeline detail:** LayoutLMv3 is not itself an OCR engine — it's a token
  classifier that requires pre-extracted words + bounding boxes as input (typically from
  Tesseract or a similar OCR engine) before it can tag each token with a CORD/SROIE entity
  label. That means a LayoutLMv3-based approach always needs a *separate* OCR step wired in
  front of it, adding a pipeline stage and another dependency.

### Donut (Document Understanding Transformer)
- Official repo: https://github.com/clovaai/donut. Paper: Kim et al., *OCR-free Document
  Understanding Transformer*, ECCV 2022, arXiv:2111.15664
  (https://arxiv.org/abs/2111.15664 / https://arxiv.org/pdf/2111.15664).
- License: **MIT** (confirmed via direct fetch of the repo's README, which states the
  MIT terms).
- Architecture/size: Swin Transformer (Swin-B, layer config `{2,2,14,2}`) visual encoder + the
  first 4 layers of a BART decoder. Multiple independent search-engine summaries of the paper's
  own comparison table converge on **~143M parameters** for `donut-base`; I was not able to
  directly quote this from the PDF itself (both `arxiv.org/pdf/...` and an `ar5iv`/reader-proxy
  fetch of it failed to return full body text), so this number should be treated as
  paper-sourced-via-secondary-aggregation rather than a directly-quoted primary figure — flagging
  this rather than presenting it as fully verified.
- **Official pretrained + fine-tuned checkpoints exist directly for CORD**, published by the
  `naver-clova-ix` org on Hugging Face: `donut-base`, `donut-base-finetuned-cord-v2`,
  `donut-base-finetuned-cord-v1`, `donut-base-finetuned-cord-v1-2560` (plus unrelated-task
  checkpoints: `-docvqa`, `-rvlcdip`, `-zhtrainticket`, `-kuzushiji`). Confirmed by listing the
  `naver-clova-ix` HF org page directly.
- **No official `donut-base-finetuned-sroie` checkpoint exists.** Only third-party/community
  fine-tunes were found (e.g. `HariNurd/donut-base-sroie`, `sam749/donut-base-finetuned-sroie-v2`,
  `unstructuredio/donut-base-sroie`) — confirmed absent from the official org listing.
- Reported inference speed: the paper itself reports **~0.7 sec/image on CORD (91.3% field
  accuracy)**, ~0.6s on Train Ticket, ~0.75s on RVL-CDIP, ~0.78s on DocVQA — but these numbers
  were measured **on a single P40 GPU**, per the paper (confirmed via search-engine synthesis of
  the paper's benchmark table, not a direct PDF quote — PDF fetch was blocked as noted above).
  **The Donut paper/repo does not report a CPU inference speed anywhere I could confirm** —
  stating this explicitly per the task instructions rather than assuming CPU performance scales
  linearly from the GPU number.
- Donut is OCR-free end-to-end: it takes a raw receipt image and directly decodes a structured
  JSON/XML-like token sequence following the *fine-tuned dataset's own schema* — for
  `donut-base-finetuned-cord-v2` that means the output keys are literally CORD's `menu.nm`,
  `menu.price`, `sub_total.*`, `total.*` fields, with no separate OCR step needed.

---

## Date extraction: native support vs. regex/heuristic pass

Cross-referencing sections above directly answers this:

- **CORD's schema has no `date` entity** (verified: full 30-class list above has none). Any
  model trained/fine-tuned on CORD — LayoutLMv3-CORD or Donut-CORD alike — **cannot output a
  date field**, because the field was never in its training labels. This applies regardless of
  which extraction model is used, since the limitation is in the dataset schema, not the model
  architecture.
- **SROIE's schema does include `date`** as 1 of its 4 entity types (`company`, `date`,
  `address`, `total`). A model properly fine-tuned on SROIE — LayoutLMv3-SROIE (community
  checkpoints exist) — would output date as a first-class named entity directly. However, **no
  official Donut-SROIE checkpoint exists** (confirmed above), so getting Donut to emit a native
  SROIE date field would require fine-tuning it from `donut-base` yourself on SROIE's 600–626
  training receipts within the 2.5-week window — feasible in principle (Donut's own repo ships
  fine-tuning scripts/config, and downstream fine-tuning on a few hundred images is far cheaper
  than the original pretraining), but adds real schedule risk for a first deep-learning project.
- **Neither dataset's schema covers both line items and date together.** CORD has line items,
  no date. SROIE has date, no line items. There is no publicly documented single CORD/SROIE
  fine-tuned checkpoint (official or community, found in this research) that outputs both in one
  pass.
- **Practical conclusion: for this project, purchase-date extraction should not be expected to
  come "for free" out of a CORD-trained model.** It realistically needs a separate lightweight
  pass — regex or a date-parsing library (e.g. Python `dateutil`) — applied to raw OCR text
  output (from Tesseract or EasyOCR) run alongside the line-item model. This is explicitly stated
  rather than left implicit, since it directly affects the project's architecture.

---

## Recommendation

**Use CORD (not SROIE) as the primary dataset, via the official `donut-base-finetuned-cord-v2`
checkpoint for line-item name/price extraction, combined with a Tesseract OCR pass +
regex/dateutil heuristic for the purchase date.** This is the strongest fit for a CPU-only,
2.5-week college project, for four concrete reasons:

1. **License clarity.** CORD's CC BY 4.0 license is directly confirmed from the official
   GitHub repo and HF dataset card — no ambiguity, no registration wall. SROIE's license could
   not be confirmed from its primary source in this session (login-gated downloads page), and
   secondary mirrors disagree with each other (CC-BY-2.0 vs. CC-BY-4.0 claims). Building on an
   unverified license is a real risk to avoid this close to a deadline.
2. **Schema fit.** The project's core requirement — individual food line-item names — is exactly
   what CORD's `menu.nm`/`menu.price`/`menu.cnt` fields annotate, and exactly what SROIE's
   schema (company/date/address/total only, no line items) cannot provide at all. Line items are
   the harder, more central requirement of the two; date is comparatively easy to bolt on
   separately (see point 4).
3. **Zero-shot readiness.** `naver-clova-ix/donut-base-finetuned-cord-v2` is an **official,
   first-party** checkpoint (MIT licensed) that can be downloaded and run today with no
   fine-tuning required — `pip install donut-python` or `transformers`, load the model, run
   inference. Given the 2.5-week deadline, this is decisively lower-risk than the LayoutLMv3
   route, which has no official CORD/SROIE checkpoint (only unofficial community weights of
   uncertain reliability) and additionally requires standing up a *separate* OCR engine just to
   feed it words+boxes, adding a pipeline stage this project doesn't need to build. Donut is
   OCR-free end-to-end, which is the simplest architecture achievable with an existing pretrained
   model.
4. **Date is cheap to add outside the model.** Since neither dataset's schema natively covers
   both requirements, don't try to force one model to do both — run Tesseract (Apache-licensed
   scope note: actually BSD/Apache-family open source, ~4 MB/language `tessdata_fast` model,
   lightweight native binary, no PyTorch dependency, official docs show ~1–3s/page on CPU) purely
   to get raw receipt text, then apply a simple date regex/`dateutil` pass to that text. This
   avoids the schedule risk of fine-tuning Donut on SROIE yourselves, and dates are one of the
   easiest fields to extract heuristically from raw OCR text (highly regular formats), so the
   accuracy cost of not using a "native" date-entity model is low.

**Expected pipeline:** receipt photo → Donut (`donut-base-finetuned-cord-v2`) → structured JSON
of line items (name, price, qty) *in parallel with* → Tesseract raw text → regex/dateutil → date
string. Both stages run CPU-only offline (batch, not real-time), which matches the "no GPU at
runtime" constraint. This combination requires no novel model training, has two of the least
license-ambiguous, best-documented open-source components available, and is realistically
buildable well inside the Oct 15, 2026 deadline.

**Known gap to flag in the project report:** Donut's own reported inference-speed numbers
(~0.7 sec/image) were measured on a P40 GPU, not CPU (arXiv:2111.15664) — no official CPU timing
exists for Donut, so the team should benchmark `donut-base-finetuned-cord-v2` on their actual
target CPU early (week 1) to confirm it's fast enough for their use case, rather than assuming
GPU numbers translate directly.

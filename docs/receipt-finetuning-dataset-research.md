# Receipt fine-tuning dataset research

Stretch-scope research for ticket `.scratch/smart-fridge/issues/11-receipt-finetuning-dataset-research.md`. Scoped to four English-grocery-receipt candidates surfaced while resolving ticket 05 (Receipt Pipeline Architecture), none of which were covered by ticket 02's CORD/SROIE research. Goal: find a dataset (or checkpoint) that could fine-tune Donut (`donut-base-finetuned-cord-v2`) on real English receipts instead of CORD's Indonesian ones, if the stretch step is ever picked up. **Not required for v1.**

Every license/size/format claim below comes from the dataset/model's own Hugging Face API metadata (`huggingface.co/api/datasets/...` or `/api/models/...`) or the Kaggle page's own schema.org JSON-LD block, fetched directly — not from a third party's description.

## 1. `trainingdatapro/ocr-receipts-text-detection` (Kaggle) / `UniqueData/ocr-receipts-text-detection` (HF mirror)

- **License:** CC BY-NC-ND 4.0 (Attribution-NonCommercial-NoDerivatives), confirmed from both the Kaggle page's own schema.org metadata and the HF mirror's `cardData.license: cc-by-nc-nd-4.0`.
- **Size: 20 images.** The HF mirror's `dataset_info.splits` reports `num_examples: 20`, `download_size: 54,557,192 bytes` (~54.6 MB) — i.e., the whole dataset is 20 receipt photos, not 20-per-something. This is a classic TrainingDataPro/Kaggle pattern: a tiny free "teaser" of a larger dataset they sell commercially (the Kaggle page's own text says "For Commercial Usage: ... leave a request on our website" to buy the full set).
- **Annotation format:** CVAT-style polygon export, not Donut-ready. Each image has a `shapes` sequence of `{label, type, points, rotation, occluded, attributes}`, where `label` is a class index into `{0: receipt, 1: shop, 2: item, 3: date_time, 4: total}` and `attributes` carries `{name, text}` pairs for the recognized text per shape. This is raw CVAT polygon/bbox output — turning it into Donut's flat target-sequence string (e.g. `<s_item>...<s_total>...`) would require writing a conversion script, same class of work ticket 02 already flagged for SROIE-style bbox datasets.
- **Download:** The HF mirror (`UniqueData/...`) is `"private": false, "gated": false` — publicly downloadable, no login wall. The original Kaggle page requires a (free) Kaggle account to download, as all Kaggle datasets do.
- **Verdict: not usable.** 20 images is far too small to fine-tune on (CORD itself only works with 1,000, and that's already considered small), the full/useful-sized version is paywalled, and CC BY-NC-ND's "NoDerivatives" clause is legally murkier for ML training use than a plain NC license.

## 2. `albertobarnabo/synthetic-receipts-ocr` (Hugging Face)

- **License: Apache 2.0** — fully permissive, no non-commercial or attribution-chain restrictions. Confirmed via `cardData.license: apache-2.0` on the HF API.
- **Size: 32,000 synthetic receipts** (30,000 train / 2,000 eval), confirmed via the dataset card and the HF API's `size_categories: ["10K<n<100K"]` tag.
- **Locales:** 5 — US, UK, Germany, Italy, France — each with locale-correct formatting, VAT/tax structure, currency symbols, and address order. The US subset can be isolated for this project's English-grocery-receipt need.
- **Degradation:** every receipt ships as a matched pair — `image_clean` (rendered PNG) and `image_photo` (JPEG with simulated perspective distortion, uneven lighting, shadow bands, thermal-printer fade, noise, and blur) — which is a reasonable proxy for a phone-camera photo of a real receipt.
- **Annotation format:** structured JSON per receipt (merchant/address/phone/tax ID/date/time/receipt number/cashier, line items with name/qty/unit price/total/tax rate, subtotal, per-class taxes, total, payment method/tendered/change, loyalty fields), plus separate word-level bounding boxes (`words`, `words_photo`) and a homography matrix. The structured-JSON half is a straightforward scripted reformat into Donut's target-sequence tags (same kind of transform CORD's own fields went through) — no OCR/bbox-to-text step needed first, unlike candidate 1.
- **Download:** `"private": false, "gated": false` on the HF API — public, no login wall.
- **Verdict: usable — strongest candidate.** Permissive license, large scale, public download, structured JSON labels that need only a reformatting pass (not a bbox-to-text pass) to become Donut targets, and an isolable US-locale subset. Caveat: the base images are template-rendered synthetic receipts, not photos of real purchases — the `image_photo` degraded variant narrows but doesn't eliminate that domain gap.

## 3. `docjay131/receipts-ocr-dataset` (Hugging Face)

- **License: MIT** — fully permissive. Confirmed via `cardData.license: mit`.
- **Size: 230 receipt images** (`size_categories: ["n<1K"]` on the HF API), real photos of receipts from a variety of merchants.
- **Annotation format:** closest to Donut's native training shape of any candidate here — the dataset is literally two columns, `image` (JPEG) and `text` (a JSON string of the extracted fields: merchant name/address, date/time, receipt number, itemized name/qty/unit price/total, subtotal/tax/tip/total, payment method/category). Donut's own training recipe consumes exactly an (image, target-string) pair, so this needs the least reformatting work of the four.
- **Important caveat on label quality:** the dataset card states the JSON labels were **generated by Gemini**, not human-annotated or human-verified. An LLM reading a receipt photo and emitting JSON can misread amounts, invent/drop line items, or normalize dates incorrectly — any such errors get baked straight into fine-tuning. Spot-checking a sample of labels against the source images before using it would be warranted.
- **Download:** `"private": false, "gated": false` — public, no login wall, Parquet format.
- **Verdict: usable with caveats.** Real photos, permissive license, and the most directly Donut-consumable format of the four, but small (230 examples) and the labels are machine-generated rather than human-verified — best used as a small real-photo supplement/eval set alongside a larger corpus, not as the sole fine-tuning set.

## 4. `AdamCodd/donut-receipts-extract` (Hugging Face model checkpoint)

- **Base model:** `naver-clova-ix/donut-base` — the *un*-fine-tuned Donut base, not the `donut-base-finetuned-cord-v2` checkpoint this project's v1 already uses zero-shot. This matters: this checkpoint's output vocabulary/tags are its own (see below), not CORD's `menu.nm`/`menu.price`/`menu.cnt` schema, so swapping it in would mean rewriting the downstream field-extraction code that currently expects CORD's tag names.
- **Training dataset:** `AdamCodd/donut-receipts`, described on the model card (V2) as "deduplicated, manually corrected," ~1,100 receipts. **This dataset could not actually be inspected** — `huggingface.co/api/datasets/AdamCodd/donut-receipts` returns HTTP 401 ("Invalid username or password"), meaning it's private/access-restricted. So its real size, source (real vs. synthetic), and label quality can't be independently verified; the "manually corrected" claim has to be taken on the model card's word alone.
- **License: CC BY-NC-4.0** (current V2, the version on the repo's main branch) — confirmed via the HF model API (`cardData.license: cc-by-nc-4.0`). This is non-commercial-only but has no NoDerivatives clause, so it would be compatible with non-commercial college coursework (with attribution); commercial use requires contacting the author. An older V1 release was MIT but is not what's on `main` now.
- **Gating — this is the key finding for this candidate: the checkpoint is NOT freely downloadable.** The HF model API returns `"gated": "manual"` — Hugging Face requires submitting an access request that the repo owner must manually approve before the weights can be downloaded. There's no guarantee of approval or of approval speed, which undercuts the "cheaper than fine-tuning" pitch if the team can't get access in time.
- **Output format:** structured tagged sequence in Donut's usual style (`<s_receipt>`, `<s_svc>`, `<s_discount>`, `<s_phone>`, etc.) — same family of approach as CORD, different vocabulary.
- **Reported eval metrics (V2, per model card):** CER 0.0756, mean accuracy 0.895, F1 0.978, edit distance 0.145, but WER 0.557 (notably high relative to the other metrics — not explained on the card, worth independent verification before relying on it).
- **Verdict: usable with caveats, conditional on access approval.** If/when access is granted, this is a real, already-fine-tuned-on-receipts Donut checkpoint and could be a cheaper path than fine-tuning any of candidates 1–3. But it is gated (not an instant download), its training data can't be independently audited (itself gated), its tag vocabulary doesn't match this project's existing CORD-based downstream parsing, and the license is non-commercial-only. Worth requesting access opportunistically and benchmarking against the zero-shot CORD baseline if/when granted, but it shouldn't be the committed plan since approval isn't guaranteed.

## Notes / caveats

- All four findings are grounded in direct API/page reads done on 2026-10-06 (`huggingface.co/api/datasets/...`, `huggingface.co/api/models/...`, and the Kaggle page's own schema.org JSON-LD), not a third party's summary of these resources. Gating/license/size fields can change after this date — re-check before actually depending on any of these.
- None of candidates 1–3 ship data already in Donut's exact target-sequence string format out of the box; all require a scripted reformatting pass from their native JSON/polygon representation into Donut's `<s_...>` tagged-sequence target, the same class of work ticket 02 anticipated. Candidate 3's `(image, JSON-string)` shape needs the least transformation; candidate 1's CVAT-polygon shape needs the most.
- "Usable for a college coursework project" is read here as: non-commercial academic use, properly attributed, is within the license's terms. Apache 2.0 (#2) and MIT (#3) raise no questions at all; CC BY-NC-4.0 (#4's checkpoint) is fine under that reading; CC BY-NC-ND-4.0 (#1) is more debatable because of the NoDerivatives clause, but it's moot since #1 fails on size regardless.
- The strongest single candidate (#2) is still synthetic data; pairing it with a small amount of real receipt photos (#3, or the team's own photos) for eval/calibration would catch sim-to-real gaps that a synthetic-only fine-tune could miss.

## Recommendation

**Primary: `albertobarnabo/synthetic-receipts-ocr` (candidate 2) as the fine-tuning corpus, supplemented by `docjay131/receipts-ocr-dataset` (candidate 3) as a small real-photo check/eval set.** This combination is the only one of the four that's simultaneously: permissively licensed (Apache 2.0 / MIT), large enough to actually fine-tune on (32k vs. CORD's 1k), publicly downloadable with no login wall or access request, and in a structured-JSON annotation format that needs straightforward reformatting rather than a bbox/polygon-to-text rebuild. Use #2's US-locale subset as the bulk of training data, and spot-check/withhold #3's 230 real photos as a small real-world sanity check, keeping in mind its labels are Gemini-generated and not human-verified.

**Opportunistic fallback, not the committed plan:** request access to `AdamCodd/donut-receipts-extract` (candidate 4) since the checkpoint route could skip fine-tuning entirely — but its manual-approval gate means this can't be relied on to arrive in time, and its tag vocabulary would require downstream parsing changes if adopted.

**Ruled out:** `trainingdatapro/ocr-receipts-text-detection` / `UniqueData/ocr-receipts-text-detection` (candidate 1) — the free version is only 20 images (a paid-upsell teaser), too small to fine-tune on regardless of license questions.

If, when this stretch step is actually picked up, candidate 2's synthetic-to-real gap turns out to be unacceptable even with the #3 supplement, ticket 05's original fallback — the team collecting and manually labeling their own receipt photos — remains the backstop.

## References

- Kaggle, *OCR Receipts Text Detection - retail dataset* (trainingdatapro) — https://www.kaggle.com/datasets/trainingdatapro/ocr-receipts-text-detection
- Hugging Face, `UniqueData/ocr-receipts-text-detection` (dataset card + API) — https://huggingface.co/datasets/UniqueData/ocr-receipts-text-detection, https://huggingface.co/api/datasets/UniqueData/ocr-receipts-text-detection
- Hugging Face, `albertobarnabo/synthetic-receipts-ocr` (dataset card + API) — https://huggingface.co/datasets/albertobarnabo/synthetic-receipts-ocr, https://huggingface.co/api/datasets/albertobarnabo/synthetic-receipts-ocr
- Hugging Face, `docjay131/receipts-ocr-dataset` (dataset card + API) — https://huggingface.co/datasets/docjay131/receipts-ocr-dataset, https://huggingface.co/api/datasets/docjay131/receipts-ocr-dataset
- Hugging Face, `AdamCodd/donut-receipts-extract` (model card + API) — https://huggingface.co/AdamCodd/donut-receipts-extract, https://huggingface.co/api/models/AdamCodd/donut-receipts-extract
- Hugging Face, `AdamCodd/donut-receipts` (training dataset for candidate 4; access-gated, returns HTTP 401 on the API) — https://huggingface.co/datasets/AdamCodd/donut-receipts
- Prior art for comparison: `.scratch/smart-fridge/issues/02-receipt-dataset-ocr-research.md` (CORD/SROIE research), `.scratch/smart-fridge/issues/05-receipt-pipeline-architecture.md` (why real-English fine-tuning was deferred to stretch)

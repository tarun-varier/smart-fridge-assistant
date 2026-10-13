---
status: accepted
---

# Receipt Pipeline as two independent zero-shot passes, no fine-tuning for v1

We parse each receipt with two independent, parallel passes over the same image: the official `naver-clova-ix/donut-base-finetuned-cord-v2` checkpoint (used zero-shot, no fine-tuning) extracts line items as structured JSON, while Tesseract's raw OCR text feeds a regex/`dateutil` pass that extracts a single purchase date for the whole receipt. Neither branch's output feeds the other, and the one extracted date is broadcast to every line item on that receipt — receipts don't carry independent per-item dates. No custom image preprocessing (deskew, binarization, contrast correction) runs before either model; we rely on Donut's built-in image processor and Tesseract's defaults. Scope is one single-page receipt per upload; multi-page receipts and batched multi-receipt uploads are out of scope, not deferred.

This mirrors the Vision Pipeline's required-path/stretch split (ADR 0001): ship the simplest working pipeline first, add complexity only if testing proves it's needed, and keep the required path realistic for a 9-day-remaining, CPU-only, solo-implemented build.

## Considered options

- **Chaining the two branches** (e.g. feeding Tesseract's text into Donut, or using Donut's output to crop/guide Tesseract) — rejected as unnecessary complexity; the two fields (line items, date) come from unrelated parts of the receipt and don't benefit from being coupled.
- **Per-line-item date extraction** — rejected because real receipts only carry one transaction date; modeling it as per-item would misrepresent the domain.
- **Custom preprocessing (deskew/binarization) before OCR** — deferred as a stretch lever, not built now, since it's unverified whether raw phone-camera photos actually need it.
- **Fine-tuning Donut on real receipt photos** — explicitly deferred to stretch scope, tracked as its own research ticket to find a licensed, Donut-trainable dataset before committing to self-collected/labeled data. Not part of the required v1 path given the remaining timeline.

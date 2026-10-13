Type: research
Status: resolved
Assignee: Tarun Varier

## Question

**Stretch scope only** — not required for v1, not on the critical path to the Oct 15, 2026 deadline.

If/when the Receipt Pipeline Architecture ticket's (05) deferred fine-tuning stretch step gets picked up, Donut (`donut-base-finetuned-cord-v2`) should be fine-tuned on real-world English grocery-receipt photos rather than CORD's existing Indonesian receipts. A quick search while resolving ticket 05 surfaced several candidates that weren't covered by ticket 02's CORD/SROIE-scoped research, none of which are verified yet:

- `trainingdatapro/ocr-receipts-text-detection` (Kaggle) / `UniqueData/ocr-receipts-text-detection` (HF) — grocery store receipts, annotated with `item`/`store`/`date_time`/`total`
- `albertobarnabo/synthetic-receipts-ocr` (HF) — synthetic receipts, 5 locales including US, photo-degraded versions, structured KIE fields
- `docjay131/receipts-ocr-dataset` (HF) — receipt photos with structured JSON extraction labels, built for fine-tuning document-VLMs
- `AdamCodd/donut-receipts-extract` (HF) — an existing Donut checkpoint already fine-tuned on receipts by a third party

For each candidate, establish (same bar as tickets 01/02):
- License, and whether it's usable for a college coursework project
- Actual annotation format — does it ship image + structured labels in a form Donut fine-tuning can consume, or just text/bounding boxes that would need reformatting?
- Size and whether it's actually downloadable (no login wall)
- For `AdamCodd/donut-receipts-extract` specifically: what it was trained on and its license, since using it directly (rather than fine-tuning yourself) might be an even cheaper option than fine-tuning from scratch

Write findings to a Markdown file (cite sources), flag the strongest candidate (or combination), and flag explicitly if none check out — in which case the fallback is collecting and manually labeling the team's own receipt photos (ticket 05's original fallback plan).

## Answer

Findings written to `docs/receipt-finetuning-dataset-research.md`, grounded in direct Hugging Face/Kaggle API metadata (not third-party descriptions).

- **`trainingdatapro`/`UniqueData` `ocr-receipts-text-detection`** — not usable. CC BY-NC-ND 4.0, but the public HF mirror is only 20 images (a paid-upsell teaser); CVAT-polygon format would also need conversion work.
- **`albertobarnabo/synthetic-receipts-ocr`** — strongest candidate. Apache 2.0, 32k synthetic receipts (5 locales incl. US, clean + photo-degraded pairs), structured JSON needing only a reformat into Donut's tag format, public/ungated. Caveat: synthetic, not real photos.
- **`docjay131/receipts-ocr-dataset`** — usable with caveats. MIT, 230 real receipt photos as direct (image, JSON-string) pairs — least reformatting of any candidate — but labels are Gemini-generated, not human-verified, and the set is small.
- **`AdamCodd/donut-receipts-extract`** — usable with caveats, conditional on access. CC BY-NC-4.0, but gated (`"gated": "manual"`, no guaranteed approval), trained on `naver-clova-ix/donut-base` (not the CORD checkpoint this project uses) with its own tag vocabulary requiring downstream parsing changes, and its own training dataset is itself private/unverifiable.

**Recommendation:** primary = synthetic-receipts-ocr as the fine-tuning corpus, supplemented by docjay131's real photos as a small eval/calibration set; donut-receipts-extract as an opportunistic (not committed) fallback pending gate approval; the Kaggle/UniqueData candidate ruled out outright. Ticket 05's original fallback (team collects and manually labels their own receipt photos) remains the backstop if the synthetic-to-real gap proves unacceptable.

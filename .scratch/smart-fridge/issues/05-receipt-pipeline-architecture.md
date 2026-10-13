Type: grilling
Status: resolved
Assignee: Tarun Varier
Blocked by: 02

## Question

Given the OCR/extraction approach chosen in the receipt-dataset-ocr-research ticket, decide the concrete Receipt Pipeline design: which OCR engine or extraction model gets used as-is vs. fine-tuned, how item-name and purchase-date fields get pulled out of raw OCR output (model-native field extraction vs. a regex/heuristic pass), and how malformed or unreadable receipts are handled.

## Answer

**Model usage: zero-shot, no fine-tuning for v1 (required path).** `naver-clova-ix/donut-base-finetuned-cord-v2` is used as-is. Further fine-tuning on real receipt photos is an explicit stretch lever, deferred to its own research ticket (see below) rather than a committed step — mirrors the Vision Pipeline's Plan A/Plan B split (ticket 04).

**Pipeline topology: two independent parallel passes over the same single-page receipt image**, merged only at the end:
- Donut (`donut-base-finetuned-cord-v2`) → structured JSON of line items (`menu.nm`/`menu.price`/`menu.cnt`), feeding ticket 03's Category-matching.
- Tesseract raw OCR text → regex/`dateutil` pass → one purchase date for the whole receipt.

Neither branch's output feeds the other (no chaining).

**Date granularity: one date per receipt, broadcast to every line item.** Real receipts have a single transaction date; CONTEXT.md's Receipt Pipeline entry is corrected to say this explicitly rather than implying independent per-line-item dates.

**Preprocessing: none for v1.** Relies on Donut's built-in image processor and Tesseract's defaults as-is. Left as a stretch lever only if week-1 testing on real phone-camera photos shows raw images are unusable.

**Upload scope: one single-page receipt per upload.** Multi-page receipts and batch-uploading multiple receipts are explicitly out of scope (not deferred/fog) — matches the Vision Pipeline's single-photo/crop scope framing.

**Fine-tuning dataset research spun off**, since a quick search surfaced English-language grocery/receipt KIE datasets (e.g. `trainingdatapro/ocr-receipts-text-detection`, `albertobarnabo/synthetic-receipts-ocr`, `docjay131/receipts-ocr-dataset`, `AdamCodd/donut-receipts-extract`) not covered by ticket 02's CORD/SROIE-scoped research, none of which are license/schema-verified yet — see the new "Receipt fine-tuning dataset research" ticket. SROIE itself was ruled out again here: no line-item fields, unresolved license, no official Donut-SROIE checkpoint (per ticket 02).

Architecture/trade-off reasoning recorded as `docs/adr/0002-receipt-pipeline-architecture.md`. `CONTEXT.md`'s Receipt Pipeline entry updated inline to reflect the single-receipt-date and single-page-scope corrections.

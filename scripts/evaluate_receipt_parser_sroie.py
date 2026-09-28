"""Evaluate receipt_parser.py against real photographed receipts (SROIE test
split). SROIE's ground truth only has company/date/address/total, no
itemized line items, so this measures date-extraction accuracy quantitatively
and dumps extracted line items for a qualitative look, rather than scoring
item-match accuracy (that's measured on the synthetic fixtures instead, and
labeled as such).

Run with the project venv: .venv/bin/python scripts/evaluate_receipt_parser_sroie.py
"""

import json
import random
import sys
from pathlib import Path

import dateparser

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.receipt_parser import analyze_receipt  # noqa: E402

SROIE_DIR = ROOT / "data" / "receipts" / "test"
SAMPLE_SIZE = 20
SEED = 7
DATE_SETTINGS = {"DATE_ORDER": "DMY"}


def main():
    entity_files = sorted((SROIE_DIR / "entities").glob("*.txt"))
    rng = random.Random(SEED)
    sample = rng.sample(entity_files, min(SAMPLE_SIZE, len(entity_files)))

    date_hits = 0
    date_total = 0
    per_receipt = []

    for entity_path in sample:
        receipt_id = entity_path.stem
        image_path = SROIE_DIR / "img" / f"{receipt_id}.jpg"
        if not image_path.exists():
            continue
        ground_truth = json.loads(entity_path.read_text())
        gt_date_raw = ground_truth.get("date")
        gt_date = dateparser.parse(gt_date_raw, settings=DATE_SETTINGS).date() if gt_date_raw else None

        analysis = analyze_receipt(str(image_path))
        date_ok = gt_date is not None and analysis.purchase_date == gt_date
        if gt_date is not None:
            date_total += 1
            date_hits += int(date_ok)

        per_receipt.append(
            {
                "receipt_id": receipt_id,
                "gt_date": gt_date_raw,
                "gt_date_parsed": gt_date.isoformat() if gt_date else None,
                "predicted_date": analysis.purchase_date.isoformat() if analysis.purchase_date else None,
                "date_ok": date_ok,
                "extracted_lines": [item.raw_text for item in analysis.line_items][:8],
            }
        )
        print(f"{receipt_id}: gt={gt_date_raw} pred={analysis.purchase_date} ok={date_ok}")

    result = {
        "sample_size": len(per_receipt),
        "date_accuracy": date_hits / date_total if date_total else None,
        "date_hits": date_hits,
        "date_total": date_total,
        "per_receipt": per_receipt,
    }
    out_path = ROOT / "results" / "receipt_eval.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\ndate accuracy: {date_hits}/{date_total} on {len(per_receipt)} real receipts")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()

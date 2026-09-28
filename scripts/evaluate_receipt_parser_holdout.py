"""Evaluate receipt_parser.py on a fresh SROIE sample that was never looked at
while iterating on the date-extraction fixes (those were tuned against
scripts/evaluate_receipt_parser_sroie.py's seed=7 sample of 20 receipts — a
cross-model review correctly flagged that as an in-sample number, not a real
holdout). This draws a disjoint sample and reports it separately.

Run with the project venv: .venv/bin/python scripts/evaluate_receipt_parser_holdout.py
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
TUNING_SEED = 7
TUNING_SAMPLE_SIZE = 20
HOLDOUT_SEED = 99
HOLDOUT_SAMPLE_SIZE = 20
DATE_SETTINGS = {"DATE_ORDER": "DMY"}


def main():
    entity_files = sorted((SROIE_DIR / "entities").glob("*.txt"))
    tuning_sample = set(
        p.stem for p in random.Random(TUNING_SEED).sample(entity_files, min(TUNING_SAMPLE_SIZE, len(entity_files)))
    )
    remaining = [p for p in entity_files if p.stem not in tuning_sample]
    holdout_sample = random.Random(HOLDOUT_SEED).sample(remaining, min(HOLDOUT_SAMPLE_SIZE, len(remaining)))
    assert not (set(p.stem for p in holdout_sample) & tuning_sample), "holdout must not overlap the tuning sample"

    date_hits = 0
    date_total = 0
    per_receipt = []

    for entity_path in holdout_sample:
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
                "predicted_date": analysis.purchase_date.isoformat() if analysis.purchase_date else None,
                "date_ok": date_ok,
            }
        )
        print(f"{receipt_id}: gt={gt_date_raw} pred={analysis.purchase_date} ok={date_ok}")

    result = {
        "note": "disjoint holdout sample, never seen while tuning the date-extraction fixes",
        "sample_size": len(per_receipt),
        "date_accuracy": date_hits / date_total if date_total else None,
        "date_hits": date_hits,
        "date_total": date_total,
        "per_receipt": per_receipt,
    }
    out_path = ROOT / "results" / "receipt_eval_holdout.json"
    out_path.write_text(json.dumps(result, indent=2))
    print(f"\nholdout date accuracy: {date_hits}/{date_total} on {len(per_receipt)} real, never-tuned-on receipts")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()

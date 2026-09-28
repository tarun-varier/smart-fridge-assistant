"""Run receipt_parser against tests/fixtures/receipts and check against manifest.json.

Run with the project venv: .venv/bin/python scripts/verify_receipt_parser.py
"""

import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.expiry import normalize_item_name
from src.receipt_parser import analyze_receipt

FIXTURES = ROOT / "tests" / "fixtures" / "receipts"


def main():
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    total_items = 0
    matched_items = 0
    date_hits = 0

    for entry in manifest:
        image_path = FIXTURES / entry["image"]
        analysis = analyze_receipt(str(image_path))
        expected_date = date.fromisoformat(entry["purchase_date"])
        expected_items = set(entry["ground_truth_items"])

        found_names = {
            normalize_item_name(item.name_text)
            for item in analysis.line_items
            if normalize_item_name(item.name_text)
        }

        date_ok = analysis.purchase_date == expected_date
        date_hits += int(date_ok)
        matched_items += len(found_names & expected_items)
        total_items += len(expected_items)

        print(f"{entry['image']}: date_ok={date_ok} (got {analysis.purchase_date}, want {expected_date})")
        print(f"  raw lines: {[i.raw_text for i in analysis.line_items]}")
        print(f"  matched items: {found_names} (expected {expected_items})")

    print(f"\ndate accuracy: {date_hits}/{len(manifest)}")
    print(f"item match accuracy: {matched_items}/{total_items}")


if __name__ == "__main__":
    main()

"""Stdlib-only checks for src/expiry.py. Run with: python3 tests/test_expiry.py"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.expiry import estimate_expiry, normalize_item_name, suggest_recipes


def test_normalize_handles_ocr_noise():
    assert normalize_item_name("SPINACH 250G") == "spinach"
    assert normalize_item_name("Whole Milk 1L") == "milk"
    assert normalize_item_name("Bananna x6") == "banana"  # OCR/typo tolerance
    assert normalize_item_name("xyz123") is None


def test_estimate_expiry_uses_shelf_life():
    purchase = date.today() - timedelta(days=2)
    result = estimate_expiry("fresh spinach bunch", purchase)
    assert result is not None
    assert result.matched_item == "spinach"
    assert result.expiry_date == purchase + timedelta(days=5)
    assert result.days_until_expiry == 3


def test_estimate_expiry_unmatched_item_returns_none():
    assert estimate_expiry("gift card", date.today()) is None


def test_suggest_recipes_ranks_by_overlap():
    suggestions = suggest_recipes(["banana", "strawberry", "milk", "yogurt"])
    assert suggestions, "expected at least one recipe suggestion"
    top_recipe, overlap = suggestions[0]
    assert top_recipe == "fruit smoothie"
    assert set(overlap) == {"banana", "strawberry", "milk", "yogurt"}


if __name__ == "__main__":
    tests = [obj for name, obj in list(globals().items()) if name.startswith("test_")]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL {test.__name__}: {exc}")
    if failures:
        print(f"{failures} failing")
        sys.exit(1)
    print(f"{len(tests)} passed")

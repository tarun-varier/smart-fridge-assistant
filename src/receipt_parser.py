"""OCR + heuristic parsing of a grocery receipt photo into line items and a purchase date.

OCR: EasyOCR (a pretrained deep text detector + recognizer, no training needed here).
Parsing: regex for price-terminated lines, dateparser for the purchase date.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re

import dateparser

_PRICE_RE = re.compile(r"[$€£₹]?\s*(\d+[.,]\d{2})\s*$")
_QTY_PREFIX_RE = re.compile(r"^\s*\d+\s*[xX]\s*")

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr

        _reader = easyocr.Reader(["en"], gpu=False)
    return _reader


@dataclass
class ReceiptLineItem:
    raw_text: str
    name_text: str
    price: float | None


@dataclass
class ReceiptAnalysis:
    purchase_date: date | None
    line_items: list[ReceiptLineItem]


def extract_text_lines(image_path: str) -> list[str]:
    """Group EasyOCR's per-word/phrase boxes back into visual receipt rows.

    EasyOCR returns one box per detected word or short phrase, not per printed
    line, so "SPINACH 250G" and its price "2.99" come back as separate boxes
    on the same row. Cluster by vertical overlap, then read left to right.
    """
    reader = _get_reader()
    results = reader.readtext(image_path, detail=1)

    boxes = []
    for box, text, _conf in results:
        if not text.strip():
            continue
        ys = [point[1] for point in box]
        xs = [point[0] for point in box]
        boxes.append(
            {"y_min": min(ys), "y_max": max(ys), "y_center": (min(ys) + max(ys)) / 2,
             "x": min(xs), "text": text}
        )
    boxes.sort(key=lambda b: (b["y_center"], b["x"]))

    rows: list[dict] = []
    for box in boxes:
        row_height = box["y_max"] - box["y_min"] or 1
        target = next(
            (row for row in rows if abs(box["y_center"] - row["y_center"]) < row_height * 0.6),
            None,
        )
        if target is None:
            rows.append({"y_center": box["y_center"], "items": [box]})
        else:
            target["items"].append(box)
            target["y_center"] = sum(item["y_center"] for item in target["items"]) / len(target["items"])

    rows.sort(key=lambda row: row["y_center"])
    return [
        " ".join(item["text"] for item in sorted(row["items"], key=lambda b: b["x"]))
        for row in rows
    ]


_NUMERIC_DATE_RE = re.compile(r"\b\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}\b")
_TIME_SUFFIX_RE = re.compile(r"\s*[:.]?\s*\d{0,2}\s*(AM|PM)\b", re.IGNORECASE)
_DATE_SETTINGS = {"DATE_ORDER": "DMY", "PREFER_DATES_FROM": "past"}
_EARLIEST_PLAUSIBLE = date(2000, 1, 1)


def _plausible(candidate: date) -> bool:
    return _EARLIEST_PLAUSIBLE <= candidate <= date.today()


def extract_purchase_date(lines: list[str]) -> date | None:
    # Try an explicit numeric date first: it's unambiguous (given DMY, as
    # printed on Indian/Malaysian receipts) and receipts print dates this
    # way. A receipt timestamp like "10.20.37 AM" matches the same pattern,
    # so skip any match immediately followed by AM/PM.
    for line in lines:
        for match in _NUMERIC_DATE_RE.finditer(line):
            tail = line[match.end():match.end() + 8]
            if _TIME_SUFFIX_RE.match(tail):
                continue
            parsed = dateparser.parse(match.group(0), settings=_DATE_SETTINGS)
            if parsed and _plausible(parsed.date()):
                return parsed.date()

    full_text = "\n".join(lines)
    try:
        from dateparser.search import search_dates

        found = search_dates(full_text, settings=_DATE_SETTINGS)
    except Exception:
        found = None
    if found:
        # Prefer a match that actually contains digits over a fuzzy word-only
        # guess, and reject anything outside a plausible receipt date range
        # (a phone number or GST ID fuzzy-matched as a date can otherwise
        # produce a year like 1400 or 1937).
        digit_matches = [f for f in found if any(ch.isdigit() for ch in f[0])]
        for _text, parsed in digit_matches + found:
            if _plausible(parsed.date()):
                return parsed.date()

    return None


def extract_line_items(lines: list[str]) -> list[ReceiptLineItem]:
    items = []
    skip_markers = ("total", "subtotal", "tax", "change", "cash", "card", "balance")
    for line in lines:
        match = _PRICE_RE.search(line)
        if not match:
            continue
        lowered = line.lower()
        if any(marker in lowered for marker in skip_markers):
            continue
        price = float(match.group(1).replace(",", "."))
        name_part = _PRICE_RE.sub("", line).strip()
        name_part = _QTY_PREFIX_RE.sub("", name_part).strip()
        if not name_part:
            continue
        items.append(ReceiptLineItem(raw_text=line, name_text=name_part, price=price))
    return items


def analyze_receipt(image_path: str) -> ReceiptAnalysis:
    lines = extract_text_lines(image_path)
    return ReceiptAnalysis(
        purchase_date=extract_purchase_date(lines),
        line_items=extract_line_items(lines),
    )

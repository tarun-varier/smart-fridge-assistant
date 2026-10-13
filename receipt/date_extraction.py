"""Tesseract OCR + regex/dateutil purchase-date extraction (ADR 0002, pass 2 of 2).

One purchase date per receipt -- real receipts carry a single transaction
date, not independent per-line-item dates (see CONTEXT.md, Receipt Pipeline).
No custom image preprocessing; relies on Tesseract's defaults.
"""

import datetime
import re

import pytesseract
from dateutil import parser as dateutil_parser
from PIL import Image

_MONTHS = r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
_DATE_PATTERN = re.compile(
    rf"\d{{1,2}}[/\-.]\d{{1,2}}[/\-.]\d{{2,4}}"
    rf"|(?:{_MONTHS})\w*\.?\s+\d{{1,2}},?\s+\d{{2,4}}"
    rf"|\d{{1,2}}\s+(?:{_MONTHS})\w*\.?,?\s+\d{{2,4}}"
    rf"|\d{{1,2}}[/\-.](?:{_MONTHS})\w*[/\-.]\d{{2,4}}",
    re.IGNORECASE,
)


def extract_purchase_date(image: Image.Image) -> datetime.date | None:
    """Return the first parseable date found in the receipt's raw OCR text, or None.

    The regex pre-filter avoids dateutil's fuzzy mode misreading unrelated
    numbers (prices, item counts) as dates; only substrings already
    date-shaped get handed to dateutil for final parsing.
    """
    text = pytesseract.image_to_string(image.convert("RGB"))

    for match in _DATE_PATTERN.finditer(text):
        try:
            return dateutil_parser.parse(match.group(), fuzzy=True).date()
        except (ValueError, OverflowError):
            continue
    return None

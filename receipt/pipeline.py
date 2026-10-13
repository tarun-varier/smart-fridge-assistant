"""Receipt Pipeline: wires Donut line-item extraction, Tesseract date
extraction, and Category matching into one call per receipt image
(issue #6: Receipt Pipeline Architecture; issue #4: Category vocabulary &
matching; ADR 0002).

The two extraction passes are independent -- neither branch's output feeds
the other -- and the single extracted purchase date is broadcast to every
line item. No preprocessing (deskew/binarization) runs before either model.
"""

import datetime
from dataclasses import dataclass

from PIL import Image

from receipt.categories import match_category
from receipt.date_extraction import extract_purchase_date
from receipt.donut_extraction import extract_line_items


@dataclass
class ReceiptLineItem:
    raw_text: str
    category: str
    purchase_date: datetime.date | None


def run_receipt_pipeline(image: Image.Image) -> list[ReceiptLineItem]:
    """Extract line items + one purchase date from a single-page receipt
    image, matching each line item into the fixed Category vocabulary."""
    line_items = extract_line_items(image)
    purchase_date = extract_purchase_date(image)

    return [
        ReceiptLineItem(raw_text=raw, category=match_category(raw), purchase_date=purchase_date)
        for raw in line_items
    ]

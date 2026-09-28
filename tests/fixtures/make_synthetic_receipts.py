"""Render synthetic receipt images with known ground truth, for verifying the
OCR + parsing pipeline before real SROIE/CORD samples are on hand.

Run with the project venv: .venv/bin/python tests/fixtures/make_synthetic_receipts.py
"""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/liberation/LiberationMono-Regular.ttf"
OUT_DIR = Path(__file__).resolve().parent / "receipts"

RECEIPTS = [
    {
        "name": "receipt_1",
        "date_line": "Date: 03/09/2026",
        "purchase_date": "2026-09-03",
        "lines": ["SPINACH 250G       2.99", "MILK 1L            1.50", "BANANA X6           1.20"],
        "ground_truth_items": ["spinach", "milk", "banana"],
    },
    {
        "name": "receipt_2",
        "date_line": "Date: 15-09-2026",
        "purchase_date": "2026-09-15",
        "lines": ["BREAD LOAF          2.10", "CHEDDAR CHEESE      4.50", "TOMATO 500G          1.80"],
        "ground_truth_items": ["bread", "cheese", "tomato"],
    },
]


def render_receipt(spec: dict) -> Image.Image:
    width, height = 400, 300
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT_PATH, 16)
    y = 20
    draw.text((20, y), "GROCERY MART", font=font, fill="black")
    y += 30
    draw.text((20, y), spec["date_line"], font=font, fill="black")
    y += 30
    for line in spec["lines"]:
        draw.text((20, y), line, font=font, fill="black")
        y += 26
    y += 10
    draw.text((20, y), "TOTAL              5.69", font=font, fill="black")
    return image


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = []
    for spec in RECEIPTS:
        image = render_receipt(spec)
        image_path = OUT_DIR / f"{spec['name']}.png"
        image.save(image_path)
        manifest.append(
            {
                "image": image_path.name,
                "purchase_date": spec["purchase_date"],
                "ground_truth_items": spec["ground_truth_items"],
            }
        )
        print(f"wrote {image_path}")
    with open(OUT_DIR / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {OUT_DIR / 'manifest.json'}")


if __name__ == "__main__":
    main()

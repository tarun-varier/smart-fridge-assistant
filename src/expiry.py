"""Shelf-life lookup, expiry estimation, and near-expiry recipe suggestions.

Shelf-life figures are approximate fridge/pantry guidance (days from purchase),
sourced from general public food-safety guidance, not a dataset. They are a
deliberate simplification: real shelf life depends on storage temperature and
item condition at purchase, which this project doesn't model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import difflib
import re

SHELF_LIFE_DAYS: dict[str, int] = {
    "spinach": 5, "lettuce": 7, "kale": 5, "cabbage": 14,
    "broccoli": 7, "cauliflower": 7, "carrot": 21, "potato": 30,
    "onion": 30, "garlic": 60, "tomato": 7, "cucumber": 7,
    "bell pepper": 10, "capsicum": 10, "mushroom": 5, "zucchini": 7,
    "apple": 21, "banana": 5, "orange": 14, "grape": 7,
    "strawberry": 3, "blueberry": 7, "mango": 5, "pineapple": 5,
    "avocado": 5, "lemon": 21, "lime": 21, "pear": 7, "peach": 5,
    "milk": 7, "yogurt": 14, "cheese": 21, "butter": 30,
    "cream": 10, "paneer": 5, "curd": 5,
    "bread": 5, "bun": 5, "tortilla": 10,
    "chicken": 2, "fish": 2, "shrimp": 2, "beef": 3, "pork": 3,
    "egg": 21,
    "tofu": 7,
    "rice": 365, "pasta": 365, "flour": 180, "sugar": 730, "salt": 3650,
    "oats": 180, "cereal": 180,
}

CANONICAL_NAMES = sorted(SHELF_LIFE_DAYS.keys(), key=len, reverse=True)

RECIPES: dict[str, list[str]] = {
    "vegetable stir fry": ["broccoli", "carrot", "bell pepper", "onion", "garlic"],
    "fruit smoothie": ["banana", "strawberry", "blueberry", "yogurt", "milk"],
    "omelette": ["egg", "onion", "cheese", "tomato", "bell pepper"],
    "grilled cheese sandwich": ["bread", "cheese", "butter"],
    "tomato pasta": ["pasta", "tomato", "garlic", "onion"],
    "spinach salad": ["spinach", "tomato", "cucumber", "lemon"],
    "mashed potatoes": ["potato", "butter", "milk"],
    "chicken stir fry": ["chicken", "bell pepper", "onion", "broccoli"],
    "fruit salad": ["apple", "banana", "orange", "grape"],
    "vegetable curry": ["potato", "cauliflower", "tomato", "onion", "garlic"],
}


@dataclass
class ExpiryEstimate:
    matched_item: str
    expiry_date: date
    days_until_expiry: int


def normalize_item_name(raw: str) -> str | None:
    """Match a raw OCR'd item string to a canonical shelf-life entry."""
    text = re.sub(r"[^a-z\s]", " ", raw.lower())
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return None
    for name in CANONICAL_NAMES:
        if name in text:
            return name
    tokens = text.split()
    candidates = difflib.get_close_matches(text, CANONICAL_NAMES, n=1, cutoff=0.7)
    if candidates:
        return candidates[0]
    for token in tokens:
        candidates = difflib.get_close_matches(token, CANONICAL_NAMES, n=1, cutoff=0.8)
        if candidates:
            return candidates[0]
    return None


def estimate_expiry(raw_item_name: str, purchase_date: date) -> ExpiryEstimate | None:
    matched = normalize_item_name(raw_item_name)
    if matched is None:
        return None
    expiry = purchase_date + timedelta(days=SHELF_LIFE_DAYS[matched])
    days_left = (expiry - date.today()).days
    return ExpiryEstimate(matched_item=matched, expiry_date=expiry, days_until_expiry=days_left)


def suggest_recipes(expiring_items: list[str], top_n: int = 3) -> list[tuple[str, list[str]]]:
    """Rank recipes by how many expiring items they use, most matches first."""
    expiring_set = {item.lower() for item in expiring_items}
    scored = []
    for recipe, ingredients in RECIPES.items():
        overlap = [ing for ing in ingredients if ing in expiring_set]
        if overlap:
            scored.append((len(overlap), recipe, ingredients, overlap))
    scored.sort(key=lambda row: row[0], reverse=True)
    return [(recipe, overlap) for _, recipe, _, overlap in scored[:top_n]]

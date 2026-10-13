"""Food Item state (CONTEXT.md: Food Item) for the Streamlit demo (issue
#8: Streamlit demo structure).

At most one Food Item per Category; a new Receipt Pipeline reading
replaces it outright (new purchase, new instance) rather than merging.
The Vision Pipeline is reactive only -- it can confirm/override an
existing Food Item's Visual Freshness Signal, but never creates one.
"""

import datetime
from dataclasses import dataclass

from fridge.freshness import DateBasedSignal, date_based_signal, resolve_freshness


@dataclass
class FoodItem:
    category: str
    purchase_date: datetime.date
    visual_is_fresh: bool | None = None

    @property
    def date_signal(self) -> DateBasedSignal:
        return date_based_signal(self.category, self.purchase_date)

    @property
    def is_fresh(self) -> bool:
        return resolve_freshness(self.date_signal, self.visual_is_fresh)

    def describe(self) -> str:
        if self.visual_is_fresh is not None:
            state = "fresh" if self.visual_is_fresh else "spoiled"
            return f"Camera confirms **{state}** -- overrides the date-based estimate."
        signal = self.date_signal
        state = "fresh" if signal.is_fresh else "likely spoiled"
        return (
            f"Bought {signal.days_since_purchase} day(s) ago; {self.category} keeps "
            f"~{signal.shelf_life_days} day(s) in the fridge -- **{state}** (date-based estimate)."
        )


class FridgeState:
    def __init__(self) -> None:
        self.items: dict[str, FoodItem] = {}
        self.unrecognized: list[str] = []

    def apply_receipt(self, category: str, purchase_date: datetime.date) -> None:
        self.items[category] = FoodItem(category=category, purchase_date=purchase_date)

    def apply_vision(self, category: str, is_fresh: bool) -> None:
        """No-op if the Category has no existing Food Item -- the Vision
        Pipeline only confirms an existing Date-Based signal, it never
        establishes a Food Item on its own."""
        item = self.items.get(category)
        if item is not None:
            item.visual_is_fresh = is_fresh

    def add_unrecognized(self, raw_text: str) -> None:
        self.unrecognized.append(raw_text)

    def alerts(self) -> list[FoodItem]:
        return sorted((item for item in self.items.values() if not item.is_fresh), key=lambda i: i.category)

    def fresh_items(self) -> list[FoodItem]:
        return sorted((item for item in self.items.values() if item.is_fresh), key=lambda i: i.category)

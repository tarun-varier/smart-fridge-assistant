"""Date-Based Freshness Signal + the Visual/Date-Based conflict rule
(CONTEXT.md: Date-Based Freshness Signal, Freshness).
"""

import datetime
from dataclasses import dataclass

from fridge.shelf_life import FRIDGE_SHELF_LIFE_DAYS


@dataclass
class DateBasedSignal:
    is_fresh: bool
    days_since_purchase: int
    shelf_life_days: int


def date_based_signal(
    category: str, purchase_date: datetime.date, today: datetime.date | None = None
) -> DateBasedSignal:
    today = today or datetime.date.today()
    days_since_purchase = (today - purchase_date).days
    shelf_life_days = FRIDGE_SHELF_LIFE_DAYS[category]
    return DateBasedSignal(
        is_fresh=days_since_purchase <= shelf_life_days,
        days_since_purchase=days_since_purchase,
        shelf_life_days=shelf_life_days,
    )


def resolve_freshness(date_signal: DateBasedSignal, visual_is_fresh: bool | None) -> bool:
    """Visual Freshness Signal wins over Date-Based on disagreement; falls
    back to the Date-Based Signal when no Visual Signal has confirmed yet."""
    if visual_is_fresh is not None:
        return visual_is_fresh
    return date_signal.is_fresh

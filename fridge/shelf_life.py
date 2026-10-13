"""Shelf-Life Table (issue #6: Shelf-Life Table; data in
docs/shelf-life-table.md).

A fixed, hardcoded fridge-days figure per Category, each collapsed to one
point value from the sourced day range as the research ticket left that
collapse to implementation.
"""

FRIDGE_SHELF_LIFE_DAYS: dict[str, int] = {
    "apple": 35,  # midpoint of FoodKeeper's 28-42 day fridge range
    "banana": 3,  # FoodKeeper's single fridge figure, once ripe
    "orange": 15,  # midpoint of FoodKeeper's 10-21 day fridge range (combined "citrus fruit" entry)
}

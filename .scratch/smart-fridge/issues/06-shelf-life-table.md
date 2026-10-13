Type: research
Status: resolved
Blocked by: 03
Assignee: Tarun Varier

## Question

For the final Category vocabulary locked in the category-vocabulary-matching ticket, compile the Shelf-Life Table: typical days-until-spoilage per Category, sourced from a credible food-safety reference (e.g. USDA FoodKeeper data or equivalent). Write findings to a Markdown file citing the source per Category, and note where you saved it.

## Answer

Findings written to `docs/shelf-life-table.md`, sourced from the USDA FSIS FoodKeeper dataset's machine-readable JSON export (data version 128), with StillTasty used only as a fallback/cross-check.

- **Apple**: 21 days pantry, 28–42 days fridge (FoodKeeper "Apples" entry, days-of-purchase fields).
- **Banana**: no FoodKeeper pantry number (qualitative "store until ripe"; StillTasty fallback: 2–5 days); 3 days fridge once ripe per FoodKeeper (StillTasty cross-check disagrees: 5–7 days). Banana's FoodKeeper fields are ripeness-timed, not purchase-timed, unlike apple/orange.
- **Orange**: 10 days pantry, 10–21 days fridge — from FoodKeeper's combined "Citrus fruit" entry (orange has no dedicated row; the entry also covers lemon, lime, grapefruit, tangerine, clementine).

Caveat for implementation: the Shelf-Life Table will need to collapse each range to one hardcoded number per category; banana's pantry cell is StillTasty's number by necessity since FoodKeeper has nothing numeric there.

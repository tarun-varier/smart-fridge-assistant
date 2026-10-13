# Shelf-life research: apple, banana, orange

Source numbers for the Shelf-Life Table (see `CONTEXT.md`), scoped to the locked 3-category vocabulary `{apple, banana, orange}` from `.scratch/smart-fridge/issues/03-category-vocabulary-matching.md`. Numbers below come from the USDA FSIS FoodKeeper dataset's machine-readable JSON export, fetched directly rather than taken from a blog that summarizes it; StillTasty is used only as a fallback/cross-check where noted.

| Category | Pantry shelf-life (days) | Fridge shelf-life (days) | Source |
|---|---|---|---|
| Apple | 21 (3 weeks) | 28–42 (4–6 weeks) | USDA FSIS FoodKeeper, "Apples" entry |
| Banana | No FoodKeeper number — store at room temp "until ripe"; StillTasty estimate: 2–5 | 3 once ripe (FoodKeeper); StillTasty cross-check: 5–7 | USDA FSIS FoodKeeper, "Bananas" entry (fridge); StillTasty (pantry estimate + fridge cross-check) |
| Orange | 10 | 10–21 | USDA FSIS FoodKeeper, "Citrus fruit" entry (covers orange, lemon, lime, grapefruit, tangerine, clementine) |

## Notes

- **Orange has no dedicated FoodKeeper row.** FoodKeeper groups orange with lemon, lime, grapefruit, tangerine, and clementine under one combined "Citrus fruit" entry (`ID 256`). The 10 / 10–21 day figures are for that whole group, not orange specifically — FoodKeeper doesn't break citrus out further.
- **Apple and orange numbers are "days of purchase" (DOP) fields.** FoodKeeper's apple and citrus-fruit rows populate the `DOP_Pantry_*` / `DOP_Refrigerate_*` columns (clock starts at purchase date), which lines up with the Date-Based Freshness Signal's "elapsed days since purchase" definition in `CONTEXT.md`. Banana instead uses the plain `Pantry_*` / `Refrigerate_*` columns, timed from ripeness rather than purchase.
- **Banana pantry has no FoodKeeper number at all.** FoodKeeper's "Bananas" row sets `Pantry_Metric` to the qualitative value `"When Ripe"` (tip: "Ripe is when this item is tender, fully developed and ready to eat") with no numeric min/max — it only gives a numeric fridge duration (3 days, "once ripe; skin will blacken"). The 2–5 day pantry figure above is StillTasty's, used as a fallback per the task's allowance for a reputable equivalent when FoodKeeper lacks a clean number.
- **FoodKeeper vs. StillTasty disagree on banana fridge days** (3 vs. 5–7) and run noticeably different on apple/orange pantry days (FoodKeeper: 21 / 10; StillTasty: ~5–7 for both). FoodKeeper is treated as authoritative throughout since it's the primary USDA dataset; StillTasty numbers are flagged, not substituted in, except for the banana pantry cell where FoodKeeper has nothing to offer.
- All ranges assume typical ripeness at purchase and refrigeration around 40°F (4°C) with normal humidity; bruising, pre-existing ripeness, and fridge conditions shift actual spoilage timing in either direction. The Shelf-Life Table implementation will need to collapse each range to one hardcoded number per category.

## References

- USDA Food Safety and Inspection Service, *FoodKeeper Data* (JSON export, data version 128, modified 2018-09-06) — https://www.fsis.usda.gov/shared/data/EN/foodkeeper.json, listed at https://catalog.data.gov/dataset/fsis-foodkeeper-data
- USDA, *FoodKeeper App* (consumer-facing front end for the same dataset) — https://www.foodsafety.gov/keep-food-safe/foodkeeper-app
- StillTasty, "How Long Do Apples Last?" — https://www.stilltasty.com/fooditems/index/16383 (cross-check only)
- StillTasty, "How Long Do Bananas Last?" — https://www.stilltasty.com/fooditems/index/16451 (pantry fallback + fridge cross-check)
- StillTasty, "How Long Do Oranges Last?" — https://www.stilltasty.com/fooditems/index/17845 (cross-check only)

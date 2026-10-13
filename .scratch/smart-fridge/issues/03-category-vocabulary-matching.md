Type: grilling
Status: resolved
Blocked by: 01, 02

## Question

Given the Vision Pipeline dataset's actual Category list (from the vision-dataset-research ticket) and the Receipt Pipeline dataset's item-naming conventions (from the receipt-dataset-ocr-research ticket), decide:

- The final, fixed Category vocabulary for this project (a subset/intersection that makes sense for both pipelines, per `CONTEXT.md`'s definition of Category)
- The text-matching approach that turns free-text receipt item names into one of those fixed Categories (e.g. fuzzy string matching, a small synonym table, or something else), including what happens when a receipt line doesn't match any known Category

## Answer

**Category vocabulary: `{apple, banana, orange}`** (3 categories), kept at this size rather than widening the Vision Pipeline dataset now. Derived by stripping the fresh/rotten prefix off the 6 classifier labels from ticket 01's chosen dataset (`freshapples`/`rottenapples` → `apple`, etc.). The classifier itself still trains and predicts all 6 fresh/rotten labels — that 6-way prediction *is* the Visual Freshness Signal — Category is a separate, derived read on that same label, not a second model output. Accepted trade-off: most real grocery receipt lines (milk, bread, chicken, spinach, …) will not match any of the 3 categories, which is an honest, demonstrable limitation for a 2.5-week coursework project rather than a blocker; widening to the 28-class stretch dataset (`muhammad0subhan/fruit-and-vegetable-disease-healthy-vs-rotten`, noted in ticket 01) stays available as stretch scope only if time allows, not reopened now.

**Matching approach:** normalize each receipt line (lowercase; strip digits, units, and common modifiers like "organic"/"fresh"), then fuzzy-match (e.g. `rapidfuzz` token-set ratio) against each Category name plus a short synonym list (e.g. apple: fuji, gala, granny smith). Exact match threshold and the full synonym-list contents are implementation-time tuning, not locked here.

**No-match / ambiguous-match handling:** a receipt line with no confident match, or a tie between categories, is flagged `unrecognized category` in the Streamlit demo rather than silently dropped or routed to a generic bucket. No Date-Based Freshness Signal is computed for it.

`CONTEXT.md`'s Category definition updated inline to reflect the derivation-from-classifier-label mechanism and the fuzzy-matching/unrecognized-category behavior.

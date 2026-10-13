# Smart Fridge / Food Waste Reduction Assistant

A multimodal CV + NLP system that tracks food items in a household fridge, estimates their freshness from two independent signals, and alerts the user before food spoils.

## Language

**Food Item**:
A single tracked instance of a food product, identified by a Category — at most one Food Item exists per Category at a time, so a new reading for a Category replaces its prior Food Item rather than coexisting alongside it. Updated by whichever pipeline (Vision or Receipt) has produced a reading for it. The unifying identity across the Vision Pipeline and the Receipt Pipeline.
_Avoid_: Product, ingredient, grocery item

**Category**:
The fixed food type a Food Item belongs to (e.g. "apple", "banana", "orange"), derived from the Vision Pipeline's classifier label set by stripping the fresh/rotten prefix (`freshapples`/`rottenapples` → `apple`). The classifier itself still predicts all 6 fresh/rotten labels — that prediction *is* the Visual Freshness Signal — but Category and Freshness are separate concepts read off that one label. Receipt text is matched into this same fixed vocabulary via fuzzy string matching against each Category name plus a short synonym list (e.g. apple: fuji, gala, granny smith); a receipt line with no confident match is flagged as unrecognized rather than dropped or bucketed — there is no open-vocabulary category and no generic fallback category.
_Avoid_: Class, label, type

**Vision Pipeline**:
Produces a Visual Freshness Signal by classifying a photo of a Food Item as fresh or spoiled (bruising, mold, discoloration). Invoked on demand to confirm or override a Food Item's existing Date-Based Freshness Signal, not run independently of one — a Food Item with no Date-Based Freshness Signal yet has nothing for the Vision Pipeline to confirm.
_Avoid_: CV pipeline, detection pipeline

**Receipt Pipeline**:
Parses a single-page photographed or digital grocery receipt via OCR, matches each line item to a Category, and produces a Date-Based Freshness Signal from the Shelf-Life Table. The purchase date is read once per receipt and applied to every line item on it — receipts don't carry independent per-item dates. Multi-page receipts and batches of multiple receipts are out of scope: one receipt image in, one purchase date out.
_Avoid_: OCR pipeline, NLP pipeline

**Visual Freshness Signal**:
A freshness reading for a Food Item produced by the Vision Pipeline from an actual photo. Reflects observed condition, not a prediction.
_Avoid_: CV result, image classification

**Date-Based Freshness Signal**:
A freshness reading for a Food Item derived from elapsed days since purchase compared against the Shelf-Life Table entry for its Category. A prediction, not an observation.
_Avoid_: Expiry estimate, age-based signal

**Shelf-Life Table**:
A fixed, hardcoded lookup of typical days-until-spoilage per Category (e.g. spinach → 5 days), used to compute the Date-Based Freshness Signal. Not learned from data.
_Avoid_: Expiry table, decay model

**Freshness**:
The current spoilage state of a Food Item: fresh or spoiled. When both a Visual Freshness Signal and a Date-Based Freshness Signal exist for the same Food Item and disagree, the Visual Freshness Signal wins — an actual photo outranks a date-based prediction.
_Avoid_: Spoilage status, condition

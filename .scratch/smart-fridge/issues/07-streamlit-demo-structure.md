Type: grilling
Status: resolved
Assignee: Tarun Varier
Blocked by: 03, 04, 05

## Question

Given the Category vocabulary/matching design, the Vision Pipeline architecture, and the Receipt Pipeline architecture, decide the Streamlit demo's concrete structure: what screens/tabs exist, the upload flow for a fridge photo and a receipt, how a unified Food Item and its Freshness (with the visual-wins conflict rule) get displayed, and what the spoilage-alert UI looks like.

## Answer

**Redirected mid-grill from an independent dual-upload design to a receipt-first, vision-as-confirmation design**, per Tarun's steer: receipts drive alerts by default; a photo (real upload or `camera_input` simulating a fridge-mounted camera) only confirms/overrides an alert already raised.

**Screens, top to bottom, single page (no tabs):**

1. **Receipt upload**: single-page receipt photo upload. Donut extracts line items → Category-match (ticket 03's fuzzy match) → Tesseract+regex extracts a purchase date into an **editable date field** (user-correctable/backdateable — doubles as the demo's way to simulate elapsed time, since a live-uploaded receipt otherwise always carries today's date). Each matched line creates/updates that Category's Food Item and computes its Date-Based Freshness Signal against the Shelf-Life Table (ticket 06).
2. **Alert list** (primary view): one row per Category with an active concern (date-based expiring/expired, or visual-confirmed spoiled). Each row has a **"Confirm with camera"** action offering both `st.camera_input` and a plain file-upload fallback. Confirming runs the Vision Pipeline for that Category and applies the already-locked visual-wins rule: visual-fresh clears the alert and moves the row to the Inventory table, badged "confirmed fresh"; visual-spoiled keeps the row in the Alert list, relabeled "confirmed spoiled" (definitive, no longer merely date-based).
3. **Inventory table** (secondary): Categories with no active concern — within shelf life, or confirmed fresh by photo. Shows both signal columns (Visual: value or "—", Date-based: value) plus the resolved Freshness.
4. **Unrecognized items** (collapsible, bottom): receipt lines that didn't fuzzy-match any of the 3 Categories — shown per ticket 03's "honest limitation," not dropped.

**Food Item lifecycle:** a Food Item can now be created and live purely on a Date-Based Freshness Signal, no photo ever required — the Vision Pipeline only runs reactively, to confirm/override an existing alert, never independently. At most one Food Item per Category at a time; a new receipt line for a Category replaces its existing Food Item rather than coexisting with it. State is session-only (`st.session_state`), no file/DB persistence.

`CONTEXT.md` updated inline: Food Item's entry now states the at-most-one-per-Category constraint explicitly; Vision Pipeline's entry now states it's invoked on demand to confirm/override a Food Item's existing Date-Based Freshness Signal rather than run independently. No ADR opened — this is a reversible UX/flow decision, not a hard-to-reverse technical commitment like the backbone/dataset choices. Exact alert threshold (how many days before expiry counts as "expiring") left as implementation-time tuning, consistent with how ticket 03 left its fuzzy-match threshold unlocked.

"""Streamlit demo (issue #8: Streamlit demo structure).

Single page: receipt upload (editable/backdateable purchase date) ->
primary Alert list (each with a "Confirm with camera" action) -> secondary
Inventory table -> collapsible Unrecognized-items section. The Vision
Pipeline is wired strictly reactive: it only confirms/overrides an alert
that the Receipt Pipeline already raised, it never runs on its own.
"""

import datetime

import streamlit as st
from PIL import Image

from fridge.state import FridgeState
from receipt.categories import UNRECOGNIZED
from receipt.pipeline import run_receipt_pipeline
from vision.infer import classify

st.set_page_config(page_title="Smart Fridge", page_icon=":ice:", layout="wide")
st.title("Smart Fridge")

if "fridge" not in st.session_state:
    st.session_state.fridge = FridgeState()
fridge: FridgeState = st.session_state.fridge

st.header("1. Upload a receipt")
receipt_file = st.file_uploader("Receipt photo or scan", type=["png", "jpg", "jpeg"])

if receipt_file is not None:
    image_bytes = receipt_file.getvalue()
    if st.session_state.get("_receipt_bytes") != image_bytes:
        with st.spinner("Reading receipt (Donut line items + Tesseract date)..."):
            st.session_state._receipt_lines = run_receipt_pipeline(Image.open(receipt_file))
        st.session_state._receipt_bytes = image_bytes

    line_items = st.session_state._receipt_lines
    extracted_date = next((li.purchase_date for li in line_items if li.purchase_date is not None), None)

    if not line_items:
        st.warning("No line items could be read from this receipt.")

    purchase_date = st.date_input(
        "Purchase date (edit if the receipt date was misread, or backdate it)",
        value=extracted_date or datetime.date.today(),
        max_value=datetime.date.today(),
    )
    if extracted_date is None and line_items:
        st.caption("No date found on the receipt -- defaulted to today; edit above if needed.")

    st.write(f"Found {len(line_items)} line item(s):")
    for li in line_items:
        label = li.category if li.category != UNRECOGNIZED else f"{UNRECOGNIZED} ({li.raw_text!r})"
        st.write(f"- {label}")

    if st.button("Add to fridge", disabled=not line_items):
        for li in line_items:
            if li.category == UNRECOGNIZED:
                fridge.add_unrecognized(li.raw_text)
            else:
                fridge.apply_receipt(li.category, purchase_date)
        st.success("Fridge updated.")

st.divider()
st.header("2. Alerts")

alerts = fridge.alerts()
if not alerts:
    st.write("No alerts.")

for item in alerts:
    with st.container(border=True):
        st.subheader(item.category.title())
        st.markdown(item.describe())

        with st.expander("Confirm with camera"):
            photo = st.camera_input("Take a photo", key=f"cam_{item.category}")
            if photo is None:
                photo = st.file_uploader(
                    "Or upload a photo", type=["png", "jpg", "jpeg"], key=f"upl_{item.category}"
                )

            if photo is not None:
                photo_bytes = photo.getvalue()
                cache_key = f"_vision_result_{item.category}"
                cached = st.session_state.get(cache_key)
                is_new_photo = cached is None or cached[0] != photo_bytes

                if is_new_photo:
                    with st.spinner("Classifying..."):
                        predicted_category, is_fresh = classify(Image.open(photo))
                    cached = (photo_bytes, predicted_category, is_fresh)
                    st.session_state[cache_key] = cached

                _, predicted_category, is_fresh = cached
                if predicted_category != item.category:
                    st.warning(f"Photo looks like {predicted_category}, not {item.category} -- not applied.")
                else:
                    fridge.apply_vision(item.category, is_fresh)
                    if is_new_photo:
                        st.rerun()

st.divider()
st.header("3. Inventory")

fresh_items = fridge.fresh_items()
if fresh_items:
    st.dataframe(
        [
            {
                "Category": item.category.title(),
                "Purchase date": item.purchase_date.isoformat(),
                "Days since purchase": item.date_signal.days_since_purchase,
                "Fridge shelf life (days)": item.date_signal.shelf_life_days,
                "Signal": "visual" if item.visual_is_fresh is not None else "date-based",
            }
            for item in fresh_items
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.write("Nothing fresh tracked yet.")

with st.expander(f"Unrecognized items ({len(fridge.unrecognized)})"):
    if fridge.unrecognized:
        for raw in fridge.unrecognized:
            st.write(f"- {raw}")
    else:
        st.write("None.")

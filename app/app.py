"""Streamlit app: fridge photo -> detected items + freshness; receipt photo ->
parsed items + expiry estimates; a merged near-expiry recipe suggestion."""

import sys
import tempfile
from datetime import date
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import classifier, expiry
from src.detector import detect_food_crops
from src.receipt_parser import analyze_receipt

st.set_page_config(page_title="Smart Fridge Assistant", page_icon="🥦", layout="wide")
st.title("Smart Fridge / Food Waste Assistant")

if "expiring_items" not in st.session_state:
    st.session_state.expiring_items = []


def save_upload(uploaded_file) -> str:
    suffix = Path(uploaded_file.name).suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getvalue())
        return tmp.name


fridge_tab, receipt_tab, inventory_tab = st.tabs(["Fridge scan", "Receipt scan", "Near-expiry inventory"])

with fridge_tab:
    st.write("Upload a fridge photo. A pretrained YOLOv8n locates candidate items; a "
             "classifier fine-tuned on the Kaggle Food Freshness Dataset labels each crop.")
    if not classifier.is_trained():
        st.warning("No trained classifier found at models/freshness_classifier.pt yet — "
                    "showing detections without freshness labels. Run scripts/train_classifier.py.")

    fridge_image = st.file_uploader("Fridge photo", type=["jpg", "jpeg", "png"], key="fridge")
    if fridge_image is not None:
        image_path = save_upload(fridge_image)
        with st.spinner("Detecting items..."):
            crops = detect_food_crops(image_path)

        loaded_classifier = classifier.load_classifier() if classifier.is_trained() else None

        cols = st.columns(min(len(crops), 4) or 1)
        for i, crop in enumerate(crops):
            with cols[i % len(cols)]:
                st.image(crop.image, caption=f"detected: {crop.class_name}", use_container_width=True)
                if loaded_classifier is not None:
                    label, confidence = classifier.classify_crop(crop.image, loaded_classifier)
                    st.metric("Freshness", label, f"{confidence:.0%} confidence")

with receipt_tab:
    st.write("Upload a receipt photo. EasyOCR extracts the text; item lines and the "
             "purchase date are parsed to estimate expiry per item.")
    receipt_image = st.file_uploader("Receipt photo", type=["jpg", "jpeg", "png"], key="receipt")
    if receipt_image is not None:
        image_path = save_upload(receipt_image)
        with st.spinner("Reading receipt..."):
            analysis = analyze_receipt(image_path)

        if analysis.purchase_date is None:
            st.warning("Couldn't find a purchase date on this receipt; using today's date.")
        purchase_date = analysis.purchase_date or date.today()
        st.caption(f"Purchase date: {purchase_date.isoformat()}")

        rows = []
        expiring_names = []
        for item in analysis.line_items:
            est = expiry.estimate_expiry(item.name_text, purchase_date)
            if est is None:
                rows.append({"item": item.name_text, "price": item.price, "expiry": "unrecognized item"})
                continue
            status = (
                f"expired {-est.days_until_expiry} days ago"
                if est.days_until_expiry < 0
                else f"{est.days_until_expiry} days left"
            )
            rows.append(
                {
                    "item": est.matched_item,
                    "price": item.price,
                    "expiry": est.expiry_date.isoformat(),
                    "status": status,
                }
            )
            if est.days_until_expiry <= 3:
                expiring_names.append(est.matched_item)

        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No item lines recognized on this receipt.")

        st.session_state.expiring_items = expiring_names

with inventory_tab:
    expiring = st.session_state.expiring_items
    if not expiring:
        st.info("Scan a receipt to see items expiring soon and get recipe ideas.")
    else:
        st.write(f"Expiring within 3 days: {', '.join(sorted(set(expiring)))}")
        suggestions = expiry.suggest_recipes(expiring)
        if suggestions:
            st.subheader("Recipe ideas to use these up")
            for recipe, overlap in suggestions:
                st.write(f"**{recipe.title()}** — uses {', '.join(overlap)}")
        else:
            st.write("No recipe match found for these items.")

"""Streamlit web UI for Autopitch.

Upload an Excel financial workbook and download a consulting-quality PPTX deck.
All pipeline logic lives in autopitch/pipeline.py — this file only renders widgets.
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from autopitch.pipeline import run_pipeline  # noqa: E402
from autopitch.models import ValidationError  # noqa: E402

st.set_page_config(page_title="Autopitch", page_icon="📊", layout="centered")

st.title("Autopitch")
st.caption("Upload a financial Excel workbook to generate a consulting-quality pitch deck.")

uploaded = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded is not None:
    if st.button("Generate Deck"):
        uploaded.seek(0)
        with st.spinner("Generating deck..."):
            try:
                pptx_bytes = run_pipeline(uploaded)
                st.success("Done!")
                output_name = uploaded.name.replace(".xlsx", "") + ".pptx"
                st.download_button(
                    label="Download PPTX",
                    data=pptx_bytes,
                    file_name=output_name,
                    mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                )
            except ValidationError as e:
                st.error(str(e))

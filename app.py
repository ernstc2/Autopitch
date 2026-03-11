"""Streamlit web UI for Autopitch.

Upload an Excel financial workbook and download a consulting-quality PPTX deck.
All pipeline logic lives in autopitch/pipeline.py — this file only renders widgets.
"""

import hashlib
import time
from io import BytesIO
from pathlib import Path

import openpyxl
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from autopitch.pipeline import run_pipeline  # noqa: E402
from autopitch.models import ValidationError  # noqa: E402

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Autopitch",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state initialization — must come before any widget rendering
# ---------------------------------------------------------------------------

for _key in ("demo_pptx", "demo_elapsed", "demo_slides", "upload_pptx", "upload_hash"):
    if _key not in st.session_state:
        st.session_state[_key] = None

# ---------------------------------------------------------------------------
# Cached demo pipeline (DEMO-02) — first click calls Claude; subsequent serve cache
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def _run_demo_pipeline() -> bytes:
    """Cached: returns PPTX bytes for the bundled Apple demo file.

    @st.cache_data ensures repeated 'Try the Demo' clicks do not re-call the
    Anthropic API — only the first invocation hits the network.
    """
    return run_pipeline(Path("demo/apple_financials.xlsx"))


# ---------------------------------------------------------------------------
# Excel template builder (UPLD-03) — used in upload section below
# ---------------------------------------------------------------------------


def _build_template_xlsx() -> bytes:
    """Build a minimal openpyxl workbook with the required sheet/column structure.

    Returns:
        Valid XLSX bytes (ZIP magic PK at offset 0).
    """
    wb = openpyxl.Workbook()

    # P&L sheet
    ws_pl = wb.active
    ws_pl.title = "P&L"
    ws_pl.append(["", "FY2022", "FY2023", "FY2024"])
    for label in [
        "Revenue",
        "COGS",
        "Operating Income",
        "Depreciation & Amortization",
        "Net Income",
    ]:
        ws_pl.append([label, "", "", ""])

    # Balance Sheet
    ws_bs = wb.create_sheet("Balance Sheet")
    ws_bs.append(["", "FY2022", "FY2023", "FY2024"])
    for label in [
        "Current Assets",
        "Current Liabilities",
        "Total Assets",
        "Total Debt",
        "Total Shareholders Equity",
    ]:
        ws_bs.append([label, "", "", ""])

    # Cash Flow
    ws_cf = wb.create_sheet("Cash Flow")
    ws_cf.append(["", "FY2022", "FY2023", "FY2024"])
    for label in ["Operating Cash Flow", "Capital Expenditures"]:
        ws_cf.append([label, "", "", ""])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# HERO SECTION (DEMO-01) — appears before any interactive widget
# ---------------------------------------------------------------------------

st.title("Autopitch")
st.markdown(
    """
Upload one Excel file. Get back a boardroom-ready consulting deck in seconds — the kind
that would take an analyst two hours to build manually.

**What it does:** Autopitch parses your P&L, Balance Sheet, and Cash Flow data, computes
key financial metrics, generates slide narrative with Claude (Anthropic), and assembles a
complete 11-slide PPTX with charts, tables, and Big 4-style formatting.

**Who it's for:** Finance professionals, founders, and analysts who want polished pitch
decks without the manual formatting grind.
"""
)

# ---------------------------------------------------------------------------
# DEMO SECTION (DEMO-02, DEMO-03, DEMO-04)
# ---------------------------------------------------------------------------

st.header("Try the Demo")
st.markdown(
    "See it in action with real **Apple FY2020–FY2024** financials. "
    "One click — no data needed."
)

if st.button("Try the Demo", type="primary"):
    if st.session_state["demo_pptx"] is None:
        t0 = time.perf_counter()
        with st.spinner("Generating deck from Apple FY2020–FY2024 data..."):
            pptx_bytes = _run_demo_pipeline()
        st.session_state["demo_pptx"] = pptx_bytes
        st.session_state["demo_elapsed"] = time.perf_counter() - t0
        st.session_state["demo_slides"] = 11

# Render download button and stats based on session_state (DEMO-03, DEMO-04)
# Rendered OUTSIDE the if-button block so it persists across reruns.
if st.session_state["demo_pptx"] is not None:
    col1, col2 = st.columns([2, 3])
    with col1:
        st.download_button(
            label="Download Demo Deck",
            data=st.session_state["demo_pptx"],
            file_name="autopitch_apple_demo.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            on_click="ignore",  # prevents rerun; available since Streamlit 1.43.0
        )
    with col2:
        elapsed = st.session_state["demo_elapsed"]
        slides = st.session_state["demo_slides"]
        st.caption(f"Generated in {elapsed:.1f}s — {slides} slides")

st.divider()

# ---------------------------------------------------------------------------
# UPLOAD SECTION (UPLD-01, UPLD-02, UPLD-03)
# ---------------------------------------------------------------------------

st.subheader("Upload Your Own Data")
st.markdown(
    "Upload an Excel workbook with your company's financials to generate a "
    "custom deck. The file must contain three sheets: **P&L**, **Balance Sheet**, "
    "and **Cash Flow**."
)

with st.expander("Format guide — required sheets and columns", expanded=False):
    st.markdown(
        """
**Three sheets required (exact names):** `P&L`, `Balance Sheet`, `Cash Flow`

**Column layout:** Column A = row labels, columns B+ = fiscal years (`FY2022`, `FY2023`, ...)

**P&L required rows:** Revenue, COGS, Operating Income, Depreciation & Amortization, Net Income

**Balance Sheet required rows:** Current Assets, Current Liabilities, Total Assets,
Total Debt, Total Shareholders Equity

**Cash Flow required rows:** Operating Cash Flow, Capital Expenditures

All values must be positive numbers in millions (e.g., 394,328 for $394B).
        """
    )

col_tmpl, col_filler = st.columns([2, 3])
with col_tmpl:
    st.download_button(
        label="Download Excel Template",
        data=_build_template_xlsx(),
        file_name="autopitch_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click="ignore",
    )

uploaded = st.file_uploader(
    "Upload your Excel workbook (.xlsx)",
    type=["xlsx"],
    help="Must contain P&L, Balance Sheet, and Cash Flow sheets.",
)

if uploaded is not None:
    if st.button("Generate My Deck"):
        uploaded.seek(0)
        file_hash = hashlib.md5(uploaded.read()).hexdigest()
        uploaded.seek(0)
        if file_hash == st.session_state["upload_hash"] and st.session_state["upload_pptx"] is not None:
            st.success("Same file — using cached result.")
        else:
            with st.spinner("Generating deck..."):
                try:
                    pptx_bytes = run_pipeline(uploaded)
                    st.session_state["upload_pptx"] = pptx_bytes
                    st.session_state["upload_hash"] = file_hash
                    st.success("Done!")
                except ValidationError as e:
                    st.error(str(e))

# Render upload download button based on session_state (persists across reruns)
if st.session_state["upload_pptx"] is not None:
    output_name = (uploaded.name.replace(".xlsx", "") + ".pptx") if uploaded else "autopitch_deck.pptx"
    st.download_button(
        label="Download PPTX",
        data=st.session_state["upload_pptx"],
        file_name=output_name,
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        on_click="ignore",
    )

st.divider()

# ---------------------------------------------------------------------------
# HOW IT'S BUILT — Tech stack (SKIL-01)
# ---------------------------------------------------------------------------

STACK = [
    ("Python", "Core language — readable, ecosystem-rich, ideal for data pipelines"),
    ("Streamlit", "UI framework — zero-frontend portfolio demo in pure Python"),
    ("Claude (Anthropic)", "LLM — generates slide narrative from computed financial metrics"),
    ("python-pptx", "Deck assembly — programmatic PPTX with Big 4 consulting aesthetics"),
    ("matplotlib", "Chart rendering — revenue/margin/FCF charts embedded as PNG in slides"),
    ("openpyxl", "Excel parsing — reads uploaded workbooks with data_only=True"),
]

st.subheader("How It's Built")
for name, rationale in STACK:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown(f"**{name}**")
    with col2:
        st.markdown(rationale)

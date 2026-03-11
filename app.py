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
    page_title="Autopitch — AI Pitch Deck Generator",
    page_icon="A",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Custom CSS — dark navy polish
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ── Import font ──────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* ── Global overrides ─────────────────────────────────── */
    html, body, [class*="css"], .stMarkdown, .stMarkdown p {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Hide Streamlit header anchor links */
    h1 a, h2 a, h3 a { display: none !important; }

    /* Center content with max-width */
    .block-container {
        max-width: 1000px !important;
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
    }

    /* ── Hero ─────────────────────────────────────────────── */
    .hero-badge {
        display: inline-block;
        background: rgba(74, 158, 255, 0.1);
        border: 1px solid rgba(74, 158, 255, 0.2);
        border-radius: 999px;
        padding: 0.3rem 0.9rem;
        font-size: 0.8rem;
        color: #4a9eff;
        font-weight: 500;
        letter-spacing: 0.03em;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-family: 'Inter', sans-serif !important;
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        line-height: 1.1 !important;
        margin-bottom: 0.75rem !important;
        letter-spacing: -0.03em !important;
    }
    .hero-title span {
        background: linear-gradient(135deg, #4a9eff 0%, #80bdff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-sub {
        font-size: 1.15rem !important;
        color: #7a8ba3 !important;
        line-height: 1.65 !important;
        margin-bottom: 0 !important;
        max-width: 640px;
    }

    /* ── Cards ────────────────────────────────────────────── */
    .card {
        background: #111d2e;
        border: 1px solid rgba(74, 158, 255, 0.1);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 1rem;
    }

    .card-sm {
        background: #111d2e;
        border: 1px solid rgba(74, 158, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 0.5rem;
        transition: border-color 0.2s;
    }
    .card-sm:hover {
        border-color: rgba(74, 158, 255, 0.3);
    }

    /* ── Feature pills ────────────────────────────────────── */
    .features-row {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        margin-top: 1.5rem;
    }
    .feature-pill {
        background: rgba(74, 158, 255, 0.08);
        border: 1px solid rgba(74, 158, 255, 0.15);
        border-radius: 10px;
        padding: 0.65rem 1rem;
        font-size: 0.85rem;
        color: #a0b4cc;
        flex: 1;
        min-width: 200px;
        text-align: center;
    }
    .feature-pill strong {
        color: #e8edf4;
    }

    /* ── Section styling ──────────────────────────────────── */
    .section-num {
        display: inline-block;
        width: 28px;
        height: 28px;
        line-height: 28px;
        text-align: center;
        border-radius: 8px;
        background: rgba(74, 158, 255, 0.12);
        color: #4a9eff;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 0.5rem;
        vertical-align: middle;
    }
    .section-heading {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        color: #e8edf4 !important;
        margin-bottom: 0.4rem !important;
        display: inline !important;
        vertical-align: middle !important;
    }
    .section-sub {
        font-size: 0.95rem;
        color: #6b7f96;
        margin-top: 0.35rem;
        margin-bottom: 1.25rem;
        line-height: 1.55;
    }

    /* ── Stat pill ────────────────────────────────────────── */
    .stat-pill {
        display: inline-block;
        background: rgba(74, 158, 255, 0.1);
        border: 1px solid rgba(74, 158, 255, 0.2);
        border-radius: 999px;
        padding: 0.35rem 1rem;
        font-size: 0.85rem;
        color: #7ec8ff;
        margin-top: 0.5rem;
    }

    /* ── Tech grid ────────────────────────────────────────── */
    .tech-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
    }
    @media (max-width: 640px) {
        .tech-grid { grid-template-columns: 1fr; }
    }
    .tech-item {
        background: rgba(74, 158, 255, 0.04);
        border: 1px solid rgba(74, 158, 255, 0.1);
        border-radius: 12px;
        padding: 1rem 1.15rem;
        transition: border-color 0.2s;
    }
    .tech-item:hover {
        border-color: rgba(74, 158, 255, 0.3);
    }
    .tech-name {
        font-weight: 600;
        font-size: 0.95rem;
        color: #e8edf4;
        margin-bottom: 0.15rem;
    }
    .tech-desc {
        font-size: 0.82rem;
        color: #6b7f96;
        line-height: 1.45;
    }

    /* ── Divider ──────────────────────────────────────────── */
    hr {
        border-color: rgba(74, 158, 255, 0.08) !important;
        margin: 2rem 0 !important;
    }

    /* ── Footer ───────────────────────────────────────────── */
    .footer {
        text-align: center;
        color: #3d4f63;
        font-size: 0.78rem;
        padding: 2.5rem 0 0.5rem 0;
        border-top: 1px solid rgba(74, 158, 255, 0.06);
        margin-top: 2rem;
    }
    .footer a { color: #4a9eff; text-decoration: none; }
    </style>
    """,
    unsafe_allow_html=True,
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


# ═══════════════════════════════════════════════════════════════════════════
# HERO SECTION (DEMO-01) — appears before any interactive widget
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    '<div class="hero-badge">AI-Powered Pitch Deck Generator</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-title">Turn financial statements<br>into <span>boardroom-ready decks</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-sub">'
    "Upload one Excel file and get back a polished 11-slide consulting deck in seconds "
    "— complete with charts, tables, and AI-written narrative."
    "</div>",
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="features-row">'
    '<div class="feature-pill"><strong>Parses</strong> P&L, Balance Sheet & Cash Flow</div>'
    '<div class="feature-pill"><strong>Generates</strong> narrative with Claude AI</div>'
    '<div class="feature-pill"><strong>Assembles</strong> PPTX with Big 4 formatting</div>'
    "</div>",
    unsafe_allow_html=True,
)

st.divider()

# ═══════════════════════════════════════════════════════════════════════════
# DEMO SECTION (DEMO-02, DEMO-03, DEMO-04)
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    '<div><span class="section-num">1</span>'
    '<span class="section-heading">Try the Demo</span></div>'
    '<div class="section-sub">'
    "Generate a full deck from real Apple FY2020\u20132024 financials. One click, no data needed."
    "</div>",
    unsafe_allow_html=True,
)

if st.button("Generate Apple Demo Deck", type="primary"):
    if st.session_state["demo_pptx"] is None:
        t0 = time.perf_counter()
        with st.spinner("Calling Claude API and building slides\u2026"):
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
            on_click="ignore",
        )
    with col2:
        elapsed = st.session_state["demo_elapsed"]
        slides = st.session_state["demo_slides"]
        st.markdown(
            f'<span class="stat-pill">Generated in {elapsed:.1f}s &mdash; {slides} slides</span>',
            unsafe_allow_html=True,
        )

st.divider()

# ═══════════════════════════════════════════════════════════════════════════
# UPLOAD SECTION (UPLD-01, UPLD-02, UPLD-03)
# ═══════════════════════════════════════════════════════════════════════════

st.markdown(
    '<div><span class="section-num">2</span>'
    '<span class="section-heading">Upload Your Own Data</span></div>'
    '<div class="section-sub">'
    "Bring your own financials. Three sheets required: P&L, Balance Sheet, and Cash Flow."
    "</div>",
    unsafe_allow_html=True,
)

with st.expander("Format guide \u2014 required sheets and columns", expanded=False):
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
            st.success("Same file \u2014 using cached result.")
        else:
            with st.spinner("Generating deck\u2026"):
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

# ═══════════════════════════════════════════════════════════════════════════
# HOW IT'S BUILT — Tech stack (SKIL-01)
# ═══════════════════════════════════════════════════════════════════════════

STACK = [
    ("Python", "Core language \u2014 readable, ecosystem-rich, ideal for data pipelines"),
    ("Streamlit", "UI framework \u2014 zero-frontend portfolio demo in pure Python"),
    ("Claude (Anthropic)", "LLM \u2014 generates slide narrative from computed financial metrics"),
    ("python-pptx", "Deck assembly \u2014 programmatic PPTX with Big 4 consulting aesthetics"),
    ("matplotlib", "Chart rendering \u2014 revenue/margin/FCF charts embedded as PNG in slides"),
    ("openpyxl", "Excel parsing \u2014 reads uploaded workbooks with data_only=True"),
]

st.markdown(
    '<div><span class="section-num">3</span>'
    '<span class="section-heading">How It\'s Built</span></div>'
    '<div class="section-sub">The tools and libraries under the hood.</div>',
    unsafe_allow_html=True,
)

tech_html = '<div class="tech-grid">'
for name, rationale in STACK:
    tech_html += (
        f'<div class="tech-item">'
        f'<div class="tech-name">{name}</div>'
        f'<div class="tech-desc">{rationale}</div>'
        f"</div>"
    )
tech_html += "</div>"
st.markdown(tech_html, unsafe_allow_html=True)

st.markdown(
    '<div class="footer">'
    "Built by Chris"
    "</div>",
    unsafe_allow_html=True,
)

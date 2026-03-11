---
phase: 06-demo-first-ui
verified: 2026-03-11T00:00:00Z
status: human_needed
score: 8/8 must-haves verified
human_verification:
  - test: "Navigate to the live Streamlit Cloud URL and confirm the hero section is visible before scrolling or clicking anything"
    expected: "st.title 'Autopitch' and descriptive markdown paragraph visible in viewport before any buttons"
    why_human: "Layout rendering and viewport fold position cannot be verified statically"
  - test: "Click 'Try the Demo' and observe the download button behaviour after generation completes"
    expected: "Download button remains visible after clicking it; does not disappear on rerun"
    why_human: "on_click='ignore' rerun suppression only verifiable in a live Streamlit session"
  - test: "Upload a valid Excel file and generate a custom deck, then interact with another widget"
    expected: "Upload download button persists across reruns; session_state['upload_pptx'] survives widget interactions"
    why_human: "Session state persistence across reruns requires a live Streamlit session"
  - test: "Open the format guide expander and read its content"
    expected: "Expander expands cleanly, shows three sheet names, column layout, and required row labels in a readable format"
    why_human: "Expander rendering and readability are visual concerns"
  - test: "Download the Excel template and open it in Excel or Google Sheets"
    expected: "File opens successfully with three sheets (P&L, Balance Sheet, Cash Flow) and correct row labels pre-populated"
    why_human: "File integrity beyond PK magic bytes and openpyxl parse requires real Excel validation"
  - test: "View the 'How It's Built' section on desktop and mobile viewport"
    expected: "Six technology entries are readable in a two-column layout with bold tech name and rationale"
    why_human: "Column layout rendering and readability are visual concerns"
---

# Phase 6: Demo-First UI Verification Report

**Phase Goal:** A portfolio visitor who arrives at the live URL with no data can click one button and see a generated consulting deck, then optionally upload their own data — and the page clearly communicates what the tool does and how it was built
**Verified:** 2026-03-11
**Status:** human_needed — all automated checks pass; 6 items need live-session confirmation
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | A visitor sees a hero section explaining what Autopitch does before any interactive element | VERIFIED | `st.title("Autopitch")` at line 107; first widget (`st.button`) at line 132; hero precedes widget confirmed by structural test |
| 2 | Clicking "Try the Demo" generates a deck from bundled Apple data and presents a download button | VERIFIED | `@st.cache_data` wraps `_run_demo_pipeline()` which calls `run_pipeline(Path("demo/apple_financials.xlsx"))`; `demo/apple_financials.xlsx` confirmed present on disk |
| 3 | The download button does not disappear after clicking it (session state persistence) | VERIFIED | `on_click="ignore"` present 3 times in app.py; download button rendered outside `if st.button()` block, conditioned on `st.session_state["demo_pptx"] is not None`; needs live-session human confirmation |
| 4 | Elapsed time and slide count are displayed next to the download button after generation | VERIFIED | `st.caption(f"Generated in {elapsed:.1f}s — {slides} slides")` at line 155; `demo_elapsed` and `demo_slides` stored in session_state |
| 5 | A visitor can upload their own Excel file using clearly labelled instructions | VERIFIED | `st.file_uploader("Upload your Excel workbook (.xlsx)", type=["xlsx"])` present; surrounding markdown references three required sheets |
| 6 | An expandable format guide shows required sheets and columns | VERIFIED | `st.expander("Format guide — required sheets and columns", expanded=False)` present; content includes `P&L`, `Balance Sheet`, `Cash Flow`, `FY2022`, `Revenue`, `Operating Income` |
| 7 | A downloadable Excel template is available with correct structure | VERIFIED | `_build_template_xlsx()` returns bytes with PK magic header; openpyxl confirms all three sheets with correct row labels (tested in `test_template_xlsx_has_required_sheets`) |
| 8 | A tech stack section shows 6 technologies with one-sentence rationale per tool | VERIFIED | `STACK` list contains all 6 entries (Python, Streamlit, Claude, python-pptx, matplotlib, openpyxl) each with rationale string; rendered via `st.columns([1, 4])` |

**Score:** 8/8 truths verified by automated checks

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app.py` | Complete four-section portfolio page with hero, demo, upload, and tech stack | VERIFIED | 248 lines; all four sections present and substantive; no stubs or placeholders |
| `tests/test_ui.py` | Automated verification of DEMO-01 through DEMO-04, UPLD-01 through UPLD-03, SKIL-01 | VERIFIED | 18 tests across 6 test classes; all 18 pass |
| `demo/apple_financials.xlsx` | Bundled Apple demo data for one-click demo | VERIFIED | File present at `demo/apple_financials.xlsx` |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `app.py` | `autopitch/pipeline.py` | `@st.cache_data` wrapped `_run_demo_pipeline()` | WIRED | `return run_pipeline(Path("demo/apple_financials.xlsx"))` at line 50 |
| `app.py` | `demo/apple_financials.xlsx` | Path reference in cached demo function | WIRED | `"demo/apple_financials"` literal confirmed in source; file confirmed on disk |
| `app.py` | `st.session_state` | `demo_pptx`, `demo_elapsed`, `demo_slides` keys | WIRED | Initialization guard at lines 34-36; all three keys written after pipeline call; read for conditional render |
| `app.py` | `openpyxl.Workbook` | `_build_template_xlsx()` function | WIRED | `openpyxl.Workbook()` at line 64; three sheets created with correct labels; returns `buf.getvalue()` bytes |
| `app.py` | `autopitch/pipeline.py` | `run_pipeline(uploaded)` for custom upload path | WIRED | `pptx_bytes = run_pipeline(uploaded)` at line 209; wrapped in `try/except ValidationError` |

All 5 key links confirmed wired.

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| DEMO-01 | 06-01-PLAN | Hero/landing section explains Autopitch before interactive elements | SATISFIED | `st.title("Autopitch")` + descriptive markdown at lines 107-120; hero at line 107, first button at line 132 |
| DEMO-02 | 06-01-PLAN | One-click "Try the Demo" generates deck from bundled Apple data | SATISFIED | `@st.cache_data _run_demo_pipeline()` calls `run_pipeline(Path("demo/apple_financials.xlsx"))` |
| DEMO-03 | 06-01-PLAN | Generated deck bytes persist across reruns via session_state | SATISFIED | `on_click="ignore"` + download button outside `if st.button()` + `session_state["demo_pptx"] is not None` guard |
| DEMO-04 | 06-01-PLAN | Generation stats displayed after deck creation | SATISFIED | `st.caption(f"Generated in {elapsed:.1f}s — {slides} slides")` reads both session_state keys |
| UPLD-01 | 06-02-PLAN | File uploader with clear instructions for custom Excel data | SATISFIED | `st.file_uploader(..., type=["xlsx"])` with instructional markdown referencing three sheets |
| UPLD-02 | 06-02-PLAN | In-app format guide (expandable accordion) with sheet names and column structure | SATISFIED | `st.expander("Format guide — required sheets and columns")` with full TEMPLATE_FORMAT.md content |
| UPLD-03 | 06-02-PLAN | Downloadable Excel template with correct MIME type and binary handling | SATISFIED | `_build_template_xlsx()` returns PK-valid XLSX bytes; `st.download_button` with correct XLSX MIME type and `on_click="ignore"` |
| SKIL-01 | 06-02-PLAN | Tech stack section displaying 5-6 technologies with one-line rationale | SATISFIED | `STACK` list with 6 entries rendered via `st.columns([1, 4])`; all required technologies present |

No orphaned requirements: REQUIREMENTS.md traceability table maps only DEMO-01 through DEMO-04, UPLD-01 through UPLD-03, and SKIL-01 to Phase 6. All 8 IDs accounted for.

---

### Anti-Patterns Found

No anti-patterns found in `app.py`:
- Zero TODO/FIXME/HACK/PLACEHOLDER comments
- No empty handlers (`() => {}` or `lambda: None`)
- No stub returns (`return {}`, `return []`, `return null`)
- No console.log-only implementations
- All four sections are substantive implementations, not scaffolding

---

### Human Verification Required

The following 6 items cannot be confirmed programmatically and require a live Streamlit session at the deployed URL:

#### 1. Hero Section Visual Position

**Test:** Navigate to the live Streamlit Cloud URL without scrolling or clicking.
**Expected:** `st.title("Autopitch")` and the descriptive paragraph are visible in the initial viewport before any buttons.
**Why human:** Viewport fold position and rendering order depend on browser window size and Streamlit's layout engine.

#### 2. Demo Download Button Persistence

**Test:** Click "Try the Demo", wait for generation, then click any other widget (e.g., the format guide expander).
**Expected:** The "Download Demo Deck" button remains visible after any subsequent widget interaction.
**Why human:** `on_click="ignore"` suppression of reruns can only be observed in a live Streamlit session; static analysis confirms the pattern is correctly applied but not that Streamlit honours it.

#### 3. Upload Download Button Persistence

**Test:** Upload a valid `.xlsx` file, click "Generate My Deck", then interact with another widget.
**Expected:** The "Download PPTX" button remains visible after any subsequent interaction.
**Why human:** Same session-state persistence concern as item 2.

#### 4. Format Guide Expander Readability

**Test:** Click the "Format guide — required sheets and columns" expander.
**Expected:** Expander opens, content is readable with clear headings for each sheet and row label list.
**Why human:** Markdown rendering and layout readability are visual concerns.

#### 5. Downloaded Template Opens Correctly in Excel

**Test:** Click "Download Excel Template" and open the file in Excel or Google Sheets.
**Expected:** File opens with three sheets labelled `P&L`, `Balance Sheet`, `Cash Flow`; row labels are pre-populated in column A.
**Why human:** Real Excel validation goes beyond the PK magic byte and openpyxl parse already confirmed programmatically.

#### 6. Tech Stack Section Column Layout

**Test:** View the "How It's Built" section on both desktop and a narrowed viewport.
**Expected:** Six technology entries are readable with bold tech name on the left and rationale on the right in a two-column layout.
**Why human:** `st.columns([1, 4])` rendering and proportions are visual concerns.

---

## Gaps Summary

No gaps. All 8 automated must-haves are verified. The phase goal is functionally complete — the codebase has all required structure, wiring, and tests. Six items are flagged for human confirmation of live-session behaviour (session state persistence, visual layout, and file download UX), which is standard for a Streamlit UI phase.

Commits match SUMMARY claims exactly:
- `f1369de` — RED: 18 failing UI tests
- `ee72f5f` — GREEN: app.py rewrite, all tests pass
- `60ffbac` — UPLD/SKIL tests added (Plan 02)
- `e1cb892` — docs commit completing Phase 06

Full test suite: **80/80 passed** (28.83s)

---

_Verified: 2026-03-11_
_Verifier: Claude (gsd-verifier)_

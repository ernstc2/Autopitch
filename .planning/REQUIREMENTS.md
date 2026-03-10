# Requirements: Autopitch

**Defined:** 2026-03-09
**Core Value:** A user uploads one Excel file and gets back a boardroom-ready consulting deck in seconds — the kind that would take an analyst 2+ hours to build manually.

## v1 Requirements

### Data Input

- [x] **INPT-01**: User can provide a 3-sheet Excel workbook (sheets: P&L, Balance Sheet, Cash Flow) as input
- [x] **INPT-02**: Tool validates input structure and surfaces clear, actionable error messages before processing
- [x] **INPT-03**: Parser accepts both file paths (CLI) and BinaryIO streams (Streamlit) via a single interface
- [x] **INPT-04**: Repo includes a sample Excel file populated with real public company financials (Apple or Microsoft)
- [x] **INPT-05**: Excel input schema is documented in TEMPLATE_FORMAT.md (column names, row labels, sign conventions, multi-year layout)

### Metrics Engine

- [x] **METR-01**: Tool computes year-over-year revenue growth (%) for all available periods
- [x] **METR-02**: Tool computes gross margin, EBITDA margin, and net margin for all available periods
- [x] **METR-03**: Tool computes working capital and current ratio from balance sheet data
- [x] **METR-04**: Tool computes debt-to-equity ratio, return on equity (ROE), and return on assets (ROA)
- [x] **METR-05**: Tool computes free cash flow (operating cash flow minus capex)

### Chart Generation

- [x] **CHRT-01**: Tool generates bar/column charts for revenue and expense trends across periods
- [x] **CHRT-02**: Tool generates line charts for margin trends (gross, EBITDA, net) over time
- [x] **CHRT-03**: Tool generates a waterfall chart for P&L bridge (revenue → gross profit → EBITDA → net income)
- [x] **CHRT-04**: All charts use a consistent Big 4 color palette (navy, teal, light gray) at 150+ DPI as embedded images
- [x] **CHRT-05**: Tool generates a KPI scorecard visual summarizing 8-10 key metrics in a single view

### Deck Assembly

- [x] **DECK-01**: Output deck includes a title slide with company name, period covered, and generation date
- [x] **DECK-02**: Output deck includes an executive summary slide with 3-5 top-line financial highlights
- [x] **DECK-03**: Output deck includes a P&L section (3-4 slides): revenue trends, margin analysis, expense breakdown
- [x] **DECK-04**: Output deck includes a Balance Sheet section (2-3 slides): asset composition, working capital, leverage
- [x] **DECK-05**: Output deck includes a Cash Flow section (2-3 slides): OCF/investing/financing breakdown, free cash flow
- [x] **DECK-06**: Output deck includes a KPI scorecard slide
- [x] **DECK-07**: All slides include consistent footer (company name, date) and slide numbers
- [x] **DECK-08**: Deck uses Deloitte/PwC-style aesthetic: navy/teal color blocks, clean whitespace, professional fonts

### AI Narrative

- [x] **NARR-01**: Tool generates insight-first slide titles via Claude API (e.g. "Revenue grew 18% — services mix the primary driver" not "Revenue Trends")
- [x] **NARR-02**: Tool generates 2-3 bullet narrative commentary per deck section using Claude API
- [x] **NARR-03**: Narrative generation uses a single Claude API call per deck run, passing all computed metrics as structured JSON
- [x] **NARR-04**: System prompt and one-shot example enforce consulting-voice output (analytical, forward-looking, not descriptive)
- [x] **NARR-05**: Tool falls back gracefully to placeholder commentary when ANTHROPIC_API_KEY is not set

### Interfaces

- [ ] **INTF-01**: User can run the tool via CLI: `python generate.py financials.xlsx` outputting a `.pptx` file
- [ ] **INTF-02**: User can run the tool via Streamlit web UI: upload Excel, click generate, download PPTX
- [ ] **INTF-03**: CLI and Streamlit UI both call an identical shared `run_pipeline()` function — no logic duplication
- [ ] **INTF-04**: README documents installation, usage (CLI + UI), Excel format requirements, and API key setup

## v2 Requirements

### Extended Analysis

- **EXTD-01**: Multi-period trend analysis (3-5 year comparison, not just YoY)
- **EXTD-02**: Industry benchmark comparison overlays on charts
- **EXTD-03**: Ratio trend lines on balance sheet slides

### Output Formats

- **OUTP-01**: PDF export option alongside PPTX
- **OUTP-02**: Configurable slide count / section selection

### Data Sources

- **DATA-01**: Direct SEC EDGAR / Yahoo Finance data fetch (no Excel required)
- **DATA-02**: Multi-company side-by-side comparison deck

## Out of Scope

| Feature | Reason |
|---------|--------|
| Multi-company comparison | Doubles complexity for v1; single-company tells the complete story |
| Real-time data fetching | Static Excel keeps the tool stateless and avoids auth/API complexity |
| Custom branding / white-labeling | One polished template is the portfolio goal |
| User authentication | Not needed for local/demo tool |
| Mobile-responsive UI | Not relevant for a desktop financial analysis tool |
| Native python-pptx charts | Waterfall chart unavailable in native API; matplotlib-as-images used for all charts |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INPT-01 | Phase 1 | Complete |
| INPT-02 | Phase 1 | Complete |
| INPT-03 | Phase 1 | Complete |
| INPT-04 | Phase 1 | Complete |
| INPT-05 | Phase 1 | Complete |
| METR-01 | Phase 1 | Complete |
| METR-02 | Phase 1 | Complete |
| METR-03 | Phase 1 | Complete |
| METR-04 | Phase 1 | Complete |
| METR-05 | Phase 1 | Complete |
| CHRT-01 | Phase 2 | Complete |
| CHRT-02 | Phase 2 | Complete |
| CHRT-03 | Phase 2 | Complete |
| CHRT-04 | Phase 2 | Complete |
| CHRT-05 | Phase 2 | Complete |
| DECK-01 | Phase 2 | Complete |
| DECK-02 | Phase 2 | Complete |
| DECK-03 | Phase 2 | Complete |
| DECK-04 | Phase 2 | Complete |
| DECK-05 | Phase 2 | Complete |
| DECK-06 | Phase 2 | Complete |
| DECK-07 | Phase 2 | Complete |
| DECK-08 | Phase 2 | Complete |
| NARR-01 | Phase 3 | Complete |
| NARR-02 | Phase 3 | Complete |
| NARR-03 | Phase 3 | Complete |
| NARR-04 | Phase 3 | Complete |
| NARR-05 | Phase 3 | Complete |
| INTF-01 | Phase 4 | Pending |
| INTF-02 | Phase 4 | Pending |
| INTF-03 | Phase 4 | Pending |
| INTF-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 32 total
- Mapped to phases: 32
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-09*
*Last updated: 2026-03-09 after roadmap creation*

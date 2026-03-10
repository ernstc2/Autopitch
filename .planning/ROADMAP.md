# Roadmap: Autopitch

## Overview

Autopitch transforms a single Excel workbook into a boardroom-ready consulting deck. The build follows the pipeline's hard dependency chain: validated financial data must exist before metrics can be computed, metrics must exist before charts and narrative can be generated, and both must exist before the deck can be assembled and exposed through interfaces. Four phases deliver the complete tool — each phase produces a independently verifiable output that unblocks the next.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Data Foundation** - Parse and validate a 3-sheet Excel workbook; compute all financial metrics from the validated data (completed 2026-03-10)
- [x] **Phase 2: Visual Output** - Generate all Big 4-styled charts and assemble the complete 12-15 slide PowerPoint deck (completed 2026-03-10)
- [ ] **Phase 3: AI Narrative** - Integrate Claude API to generate insight-first titles and consulting-voice commentary for every deck section
- [ ] **Phase 4: Interfaces and Polish** - Wire the pipeline to CLI and Streamlit entry points; complete README and demo data

## Phase Details

### Phase 1: Data Foundation
**Goal**: Users can provide an Excel workbook and receive either validated financial data or clear, actionable error messages — with all key financial metrics computed and ready for visualization
**Depends on**: Nothing (first phase)
**Requirements**: INPT-01, INPT-02, INPT-03, INPT-04, INPT-05, METR-01, METR-02, METR-03, METR-04, METR-05
**Success Criteria** (what must be TRUE):
  1. A correctly formatted Excel file is parsed without errors and all required line items are available for downstream use
  2. A malformed or missing-sheet Excel file produces a specific, human-readable error message before any processing occurs
  3. All 9 financial metrics (revenue growth, gross/EBITDA/net margins, working capital, current ratio, D/E, ROE, ROA, free cash flow) are computed and match known-good values for the demo dataset
  4. The demo Excel file (Apple or Microsoft) loads cleanly and produces non-null metric values for all computed fields
  5. The input schema (column names, row labels, sign conventions, multi-year layout) is documented in TEMPLATE_FORMAT.md
**Plans**: 4 plans

Plans:
- [ ] 01-01-PLAN.md — Project scaffold: autopitch package, Pydantic v2 models, pytest test stubs, TEMPLATE_FORMAT.md
- [ ] 01-02-PLAN.md — Parser + Validator: parse_workbook() with openpyxl, collect-all-errors validation gate
- [x] 01-03-PLAN.md — Metrics engine: compute_metrics() implementing all 9 KPIs with known-value tests
- [ ] 01-04-PLAN.md — Demo data + integration: Apple FY2020-FY2024 Excel file, end-to-end pipeline smoke test

### Phase 2: Visual Output
**Goal**: A complete, professional-looking 12-15 slide PowerPoint deck is generated from computed metrics — with all charts and slide layouts in place, using Big 4 aesthetic — before any AI narrative is integrated
**Depends on**: Phase 1
**Requirements**: CHRT-01, CHRT-02, CHRT-03, CHRT-04, CHRT-05, DECK-01, DECK-02, DECK-03, DECK-04, DECK-05, DECK-06, DECK-07, DECK-08
**Success Criteria** (what must be TRUE):
  1. Opening the generated PPTX in PowerPoint reveals a 12-15 slide deck with title, executive summary, P&L section (3-4 slides), Balance Sheet section (2-3 slides), Cash Flow section (2-3 slides), and KPI scorecard slide — all with consistent footers and slide numbers
  2. Every chart slide contains an embedded chart (bar/column, line, waterfall, or KPI scorecard) rendered at 150+ DPI with the navy/teal/light gray Big 4 color palette
  3. The waterfall chart correctly traces revenue → gross profit → EBITDA → net income with positive and negative bars visually distinct
  4. Slide layouts use Deloitte/PwC-style aesthetic: navy/teal color blocks, clean whitespace, professional fonts (Calibri or Arial), consistent heading and body text sizing
**Plans**: 4 plans

Plans:
- [x] 02-01-PLAN.md — Scaffold: install python-pptx + matplotlib, create theme.py constants, write failing test stubs for all 13 requirements
- [x] 02-02-PLAN.md — Charts module: implement charts.py (bar, line, waterfall, KPI scorecard) — CHRT-01..05 GREEN
- [x] 02-03-PLAN.md — Deck assembly: implement deck.py with build_deck() — DECK-01..08 GREEN, smoke test generates apple_demo.pptx
- [x] 02-04-PLAN.md — Human visual verification: open apple_demo.pptx, confirm Big 4 aesthetic and chart rendering

### Phase 3: AI Narrative
**Goal**: Every deck section carries Claude-generated insight-first titles and consulting-voice bullet commentary — with graceful fallback when no API key is present
**Depends on**: Phase 2
**Requirements**: NARR-01, NARR-02, NARR-03, NARR-04, NARR-05
**Success Criteria** (what must be TRUE):
  1. Slide titles read as analytical insights ("Revenue grew 18% — Services mix the primary driver") not data labels ("Revenue Trends"), when an API key is present
  2. Each financial section (P&L, Balance Sheet, Cash Flow) contains 2-3 bullet points in consulting voice — forward-looking and analytical, not descriptive
  3. The entire deck is generated with a single Claude API call per run; no per-slide API calls occur
  4. Running the tool without ANTHROPIC_API_KEY set produces a complete deck with placeholder commentary instead of an error or crash
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md � narrative.py module: NarrativeOutput model, generate_narrative(), fallback guard, SDK install
- [ ] 03-02-PLAN.md � deck.py integration: wire NarrativeOutput into build_deck(), human QA of consulting-voice output

### Phase 4: Interfaces and Polish
**Goal**: Users can generate the deck via both CLI and Streamlit web UI from a single shared pipeline; the project is fully documented and demo-ready for portfolio reviewers
**Depends on**: Phase 3
**Requirements**: INTF-01, INTF-02, INTF-03, INTF-04
**Success Criteria** (what must be TRUE):
  1. Running `python generate.py demo.xlsx` in a terminal produces a `.pptx` file in the current directory with no errors
  2. Opening the Streamlit app, uploading the demo Excel file, and clicking Generate produces a downloadable `.pptx` — without duplicating any pipeline logic in the UI layer
  3. CLI output and Streamlit output produce byte-for-byte identical PPTX files (same content, same structure) from the same input
  4. A portfolio reviewer can follow README instructions to install dependencies, configure the API key, run the demo, and understand the architecture decisions — without asking for clarification
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Foundation | 4/4 | Complete   | 2026-03-10 |
| 2. Visual Output | 4/4 | Complete   | 2026-03-10 |
| 3. AI Narrative | 0/TBD | Not started | - |
| 4. Interfaces and Polish | 0/TBD | Not started | - |

# Autopitch

## What This Is

Autopitch is a Python tool that transforms raw financial data from a standard Excel workbook (P&L, Balance Sheet, Cash Flow) into a polished, consulting-style PowerPoint deck — complete with Big 4-aesthetic charts, computed financial metrics, and Claude-generated insight-first narrative commentary. Built as a portfolio project targeting Big 4 tech consulting applications.

## Core Value

A user uploads one Excel file and gets back a boardroom-ready consulting deck in seconds — the kind that would take an analyst 2+ hours to build manually.

## Requirements

### Validated

- ✓ Accept a 3-sheet Excel workbook (P&L, Balance Sheet, Cash Flow) as input with a documented format — v1.0
- ✓ Parse and validate financial data, flagging structural issues clearly — v1.0
- ✓ Compute key financial metrics: revenue growth, gross/EBITDA/net margins, working capital, current ratio, D/E ratio, cash conversion, ROE, ROA — v1.0
- ✓ Generate a 12-15 slide Deloitte/PwC-style PowerPoint deck with professional layout — v1.0
- ✓ Produce charts per financial section (bar, line, waterfall) styled to Big 4 aesthetic — v1.0
- ✓ Use Claude API to generate insight-first slide titles and 2-3 bullet narrative commentary per section — v1.0
- ✓ Expose a CLI interface: `python generate.py financials.xlsx` — v1.0
- ✓ Expose a Streamlit web UI for browser-based upload and download — v1.0
- ✓ Include a demo Excel file using real public company financials (Apple) — v1.0
- ✓ README documents setup, usage, and design decisions for portfolio reviewers — v1.0

### Active

(No active requirements — define next milestone with `/gsd:new-milestone`)

### Out of Scope

- Multi-company comparison decks — single company focus keeps scope tight for v1
- Real-time data fetching (SEC EDGAR, Yahoo Finance) — static Excel input only; avoids auth complexity
- Custom branding / white-labeling — one polished template is the goal
- PDF export — PPTX is the standard consulting deliverable format
- User authentication — not needed for a local/demo tool
- Mobile-responsive UI — not relevant for a desktop financial analysis tool
- Native python-pptx charts — waterfall chart unavailable in native API; matplotlib-as-images approach works well

## Context

Shipped v1.0 MVP with ~3,556 LOC Python.
Tech stack: python-pptx, matplotlib, openpyxl, Pydantic v2, anthropic SDK, Streamlit.
Demo data: Apple FY2020-FY2024 financials (5 years, 3 statements).
Pipeline: parse_workbook → compute_metrics → generate_narrative → build_deck → bytes.
Interfaces: CLI (`generate.py`) and Streamlit (`app.py`), both calling shared `run_pipeline()`.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Three financial statements as input | Consultants analyze all three together; single-statement tools look like student projects | ✓ Good — covers full financial picture |
| Claude for narrative | Generates insight-first language that matches consulting deck conventions | ✓ Good — single API call, consulting voice confirmed by human QA |
| Streamlit for UI | Fastest path to an impressive browser demo without building a full web app | ✓ Good — thin wrapper, zero logic duplication |
| Public company demo data (Apple) | Real financials recognizable to interviewers, validates the tool actually works | ✓ Good — FY2020-2024 data, 5 years |
| matplotlib charts as images | Native python-pptx charts lack waterfall support; images give full visual control | ✓ Good — 150+ DPI, consistent Big 4 palette |
| Pydantic v2 frozen models | Immutable data contracts, JSON serialization for API calls, type safety | ✓ Good — zero runtime mutations |
| Optional NarrativeOutput param | Backwards-compatible API: callers opt-in without breaking existing code | ✓ Good — graceful fallback to placeholder defaults |
| Shared run_pipeline() function | Single integration layer prevents logic duplication between CLI and Streamlit | ✓ Good — INTF-03 satisfied cleanly |

## Constraints

- **Tech stack**: Python — standard in data/finance tooling, familiar to consulting tech teams
- **LLM**: Claude API — requires `ANTHROPIC_API_KEY` env var; works on low-usage tier (~$0.01/deck)
- **Output format**: `.pptx` via `python-pptx` library
- **Excel input**: `openpyxl` for parsing; input format documented in TEMPLATE_FORMAT.md
- **Charts**: `matplotlib` for chart generation, embedded into slides as PNG images
- **Web UI**: Streamlit — minimal code, impressive demo layer, no backend infrastructure needed
- **No database**: stateless tool, no persistence required

---
*Last updated: 2026-03-10 after v1.0 milestone*

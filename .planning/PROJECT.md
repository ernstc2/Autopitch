# Autopitch

## What This Is

Autopitch is a Python tool that transforms raw financial data from a standard Excel workbook (P&L, Balance Sheet, Cash Flow) into a polished, consulting-style PowerPoint deck — complete with Big 4-aesthetic charts, computed financial metrics, and Claude-generated insight-first narrative commentary. Deployed as a live portfolio demo on Streamlit Cloud with a dark navy UI, one-click demo, and guided upload experience.

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
- ✓ Demo-first landing experience for portfolio visitors — v1.1
- ✓ One-click demo with bundled Apple data — v1.1
- ✓ Upload-your-own-data option with guided instructions — v1.1
- ✓ Tech stack / skills showcase section visible in UI — v1.1
- ✓ Downloadable Excel template with format documentation — v1.1
- ✓ Streamlit Cloud deployment — v1.1
- ✓ Polished dark navy UI with custom CSS and centered layout — v1.1
- ✓ Keep-alive cron prevents Streamlit Cloud hibernation — v1.1

### Active

(None — define with `/gsd:new-milestone`)

### Out of Scope

- Multi-company comparison decks — single company focus keeps scope tight
- Real-time data fetching (SEC EDGAR, Yahoo Finance) — static Excel input only; avoids auth complexity
- Custom branding / white-labeling — one polished template is the goal
- PDF export — PPTX is the standard consulting deliverable format
- User authentication — not needed for a portfolio demo tool
- Mobile-responsive UI — not relevant for a desktop financial analysis tool
- Native python-pptx charts — waterfall chart unavailable in native API; matplotlib-as-images approach works well

## Context

Shipped v1.0 MVP (2026-03-10) and v1.1 Portfolio Demo Polish (2026-03-11).
~3,591 LOC Python, 96 tests passing.
Tech stack: python-pptx, matplotlib, openpyxl, Pydantic v2, anthropic SDK, Streamlit.
Demo data: Apple FY2020-FY2024 financials (5 years, 3 statements).
Pipeline: parse_workbook → compute_metrics → generate_narrative → build_deck → bytes.
Interfaces: CLI (`generate.py`) and Streamlit (`app.py`), both calling shared `run_pipeline()`.
Live at: https://autopitch-54x3pzywhwscvrs9jw6yx7.streamlit.app/

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Three financial statements as input | Consultants analyze all three together | ✓ Good — covers full financial picture |
| Claude for narrative | Generates insight-first consulting language | ✓ Good — single API call, consulting voice |
| Streamlit for UI | Fastest path to impressive browser demo | ✓ Good — thin wrapper, zero logic duplication |
| Public company demo data (Apple) | Real financials recognizable to interviewers | ✓ Good — FY2020-2024, 5 years |
| matplotlib charts as images | Native python-pptx charts lack waterfall | ✓ Good — 150+ DPI, consistent palette |
| Pydantic v2 frozen models | Immutable data contracts, type safety | ✓ Good — zero runtime mutations |
| Shared run_pipeline() function | Single integration layer for CLI + Streamlit | ✓ Good — prevents divergence |
| @st.cache_data on demo pipeline | Prevents duplicate Claude API calls | ✓ Good — v1.1 |
| session_state for PPTX bytes | Download button survives Streamlit reruns | ✓ Good — v1.1 |
| Custom CSS via unsafe_allow_html | config.toml too limited for dark navy design | ✓ Good — v1.1 |
| GitHub Actions keep-alive cron | Prevents Streamlit Cloud 7-day hibernation | ✓ Good — v1.1 |

## Constraints

- **Tech stack**: Python — standard in data/finance tooling
- **LLM**: Claude API — requires `ANTHROPIC_API_KEY`; ~$0.01/deck
- **Output format**: `.pptx` via `python-pptx` library
- **Excel input**: `openpyxl` for parsing; input format documented in TEMPLATE_FORMAT.md
- **Charts**: `matplotlib` for chart generation, embedded as PNG images
- **Web UI**: Streamlit — deployed on Streamlit Community Cloud
- **No database**: stateless tool, no persistence required

---
*Last updated: 2026-03-11 after v1.1 milestone*

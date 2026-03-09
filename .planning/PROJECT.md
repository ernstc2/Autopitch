# Autopitch

## What This Is

Autopitch is a Python tool that transforms raw financial data from a standard Excel workbook (P&L, Balance Sheet, Cash Flow) into a polished, consulting-style PowerPoint deck — complete with charts, computed financial metrics, and AI-generated narrative commentary. It is designed as a portfolio project targeting Big 4 tech consulting job applications, demonstrating the intersection of financial analysis automation and AI.

## Core Value

A user uploads one Excel file and gets back a boardroom-ready consulting deck in seconds — the kind that would take an analyst 2+ hours to build manually.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Accept a 3-sheet Excel workbook (P&L, Balance Sheet, Cash Flow) as input with a documented format
- [ ] Parse and validate financial data, flagging structural issues clearly
- [ ] Compute key financial metrics: revenue growth, gross/EBITDA/net margins, working capital, current ratio, D/E ratio, cash conversion, ROE, ROA
- [ ] Generate a 12-15 slide Deloitte/PwC-style PowerPoint deck with professional layout
- [ ] Produce charts per financial section (bar, line, waterfall) styled to Big 4 aesthetic
- [ ] Use Claude API to generate insight-first slide titles and 2-3 bullet narrative commentary per section
- [ ] Expose a CLI interface: `python generate.py financials.xlsx`
- [ ] Expose a Streamlit web UI for browser-based upload and download
- [ ] Include a demo Excel file using real public company financials (e.g., Apple or Microsoft)
- [ ] README documents setup, usage, and design decisions for portfolio reviewers

### Out of Scope

- Multi-company comparison decks — single company focus keeps scope tight for v1
- Real-time data fetching (SEC EDGAR, Yahoo Finance) — static Excel input only; avoids auth complexity
- Custom branding / white-labeling — one polished template is the goal
- PDF export — PPTX is the standard consulting deliverable format
- User authentication — not needed for a local/demo tool

## Context

- Portfolio project: primary audience is Big 4 tech consulting interviewers (Deloitte, PwC, EY, KPMG digital/tech practices)
- The tool should demonstrate: financial domain knowledge, Python engineering, AI integration, and output quality
- Demo data will use a well-known public company (Apple or Microsoft) sourced from annual reports — recognizable to interviewers
- Big 4 / Deloitte aesthetic: clean slides, branded color blocks (navy/teal), whitespace-heavy, chart-forward, insight-first titles
- LLM: Claude API (claude-sonnet model) for narrative generation — one call per deck with structured financial context as input
- UI: CLI for technical reviewers, Streamlit for non-technical demo — both produce identical PPTX output

## Constraints

- **Tech stack**: Python — standard in data/finance tooling, familiar to consulting tech teams
- **LLM**: Claude API — requires `ANTHROPIC_API_KEY` env var; must work on free/low-usage tier
- **Output format**: `.pptx` via `python-pptx` library
- **Excel input**: `openpyxl` or `pandas` for parsing; input format must be documented and validated
- **Charts**: `matplotlib` or `plotly` for chart generation, embedded into slides
- **Web UI**: Streamlit — minimal code, impressive demo layer, no backend infrastructure needed
- **No database**: stateless tool, no persistence required

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Three financial statements as input | Consultants analyze all three together; single-statement tools look like student projects | — Pending |
| Claude for narrative | Generates insight-first language ("Revenue grew X% driven by...") that matches consulting deck conventions | — Pending |
| Streamlit for UI | Fastest path to an impressive browser demo without building a full web app | — Pending |
| Public company demo data | Real financials (Apple/MSFT) are recognizable to interviewers and validate the tool actually works | — Pending |

---
*Last updated: 2026-03-09 after initialization*

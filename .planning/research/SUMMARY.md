# Project Research Summary

**Project:** Autopitch
**Domain:** Python financial PowerPoint automation — Excel three-statement input to Big 4-style deck with AI narrative
**Researched:** 2026-03-09
**Confidence:** MEDIUM-HIGH

## Executive Summary

Autopitch is a stateless, single-run CLI and web tool that transforms a structured Excel workbook (P&L, Balance Sheet, Cash Flow) into a professionally styled PowerPoint presentation with AI-generated insight-first narrative. The dominant pattern for this class of tool is a strict linear transformation pipeline: parse → validate → compute metrics → generate charts → generate narrative → assemble deck. The pipeline is invoked identically by both entry points (CLI and Streamlit), so all business logic lives in shared modules with neither interface containing any analytical code. This is the architecturally correct approach and the one portfolio reviewers will recognize as disciplined engineering.

The recommended stack is deliberate and minimal: openpyxl + pandas for Excel ingestion, matplotlib for chart generation (embedded as BytesIO images — never via python-pptx's limited native chart API), python-pptx for deck assembly using a pre-built `.pptx` template, and the Anthropic SDK with a single structured Claude API call per deck run. The waterfall chart — the signature consulting visualization — requires a custom matplotlib stacked-bar implementation since neither python-pptx nor matplotlib natively support the type. The AI narrative layer must be engineered to produce insight-first consulting language, not descriptive data summaries; this requires explicit persona instructions and one-shot formatting examples in the system prompt.

The two most consequential risks are data quality and prompt quality. On the data side, openpyxl's formula cell behavior (returning None when caches are unpopulated) will silently corrupt the entire downstream pipeline if not caught at parse time with a hard validation gate. On the AI side, a prompt that lacks a clear consulting persona and structured output schema will produce generic prose that undermines the portfolio impression. Both risks are solvable at their respective phase boundaries with proper defensive design — they are not architectural problems.

---

## Key Findings

### Recommended Stack

The stack is fully Python, with no compiled, browser, or Office-installation dependencies. Python 3.11 or 3.12 is required. openpyxl handles structural Excel reading (sheet discovery, cell-level validation, `data_only=True` is mandatory); pandas handles all metric computation via vectorized operations. Matplotlib renders charts to in-memory BytesIO PNG buffers at 150-200 DPI — this is the correct approach for pixel-perfect Big 4 styling and sidesteps all python-pptx native chart limitations. python-pptx v1.0 assembles the final deck, driven by a committed `.pptx` template file with named slide layouts. The Anthropic SDK makes a single Claude API call per deck run, receiving a structured JSON context and returning all slide narratives in one response. Streamlit provides the browser UI with negligible additional code. argparse (stdlib) handles the CLI.

**Core technologies:**
- `openpyxl ^3.1`: Excel structural parsing — pure-Python, no Excel installation required, `data_only=True` reads cached values not formulas
- `pandas ^2.2`: Metric computation and DataFrame representation — `.pct_change()`, `.div()`, boolean masking cover all required KPIs
- `matplotlib ^3.9`: Chart generation to BytesIO — full brand control, handles waterfall via stacked-bar, embeds cleanly in pptx via `add_picture()`
- `python-pptx ^1.0`: Deck assembly — EMU-level positioning, named placeholder access, template-driven layout
- `anthropic ^0.28` (verify): Claude API — single structured call per deck, JSON response, graceful fallback if key missing
- `streamlit ^1.35`: Browser UI — file upload, spinner, `st.download_button()`, session_state for result caching
- `python-dotenv ^1.0`: API key loading from `.env`
- `pytest ^8.x` + `pytest-cov`: Test layer for metric computation (critical for portfolio credibility)
- `black + ruff`: Formatting and linting (consulting codebases are visually clean)

**Version note:** anthropic SDK and streamlit are actively versioned. Verify latest versions via PyPI before pinning. python-pptx v1.0 (2024) changed the API from 0.x — check migration notes.

### Expected Features

The feature set is anchored on standard Big 4 financial deck conventions for a three-statement analysis. See `FEATURES.md` for the full 15-slide deck structure.

**Must have (table stakes):**
- Title slide, executive summary/key takeaways slide, section divider slides — structural minimum for a credible deck
- Revenue trend chart (bar, multi-year) — core financial narrative; every reviewer will look for this first
- Gross/EBITDA/net margin trend (line chart) — required to demonstrate P&L coverage
- Balance sheet snapshot and cash flow summary slides — validates three-statement coverage
- Key metrics KPI scorecard — computed ratios (growth %, margins, current ratio, D/E, ROE, ROA)
- Consistent Big 4 color theme (navy/teal/grey) across all slides — visual consistency is the first quality signal
- Slide numbers and footer — consulting deck standard; missing = looks like a draft
- CLI interface (`python generate.py input.xlsx`) — technical reviewers must be able to run it
- Streamlit UI for upload and download — demonstrates engineering range
- Demo Excel file with real public company data (Apple or Microsoft) — reviewers need to run it
- Input validation with clear error messages — broken tools without good errors look unfinished
- README with setup, usage, template format, architecture decisions

**Should have (differentiators for Big 4 interviews):**
- AI-generated insight-first slide titles ("Revenue grew 18% — Services mix shift the primary driver" not "Revenue Trend")
- AI narrative bullets per section (2-3 per slide, consulting voice)
- Waterfall chart for cash flow bridge — signature consulting chart type; most tools skip it
- Anomaly/flag detection fed into AI prompt context ("Gross margin compressed 4pp YoY")
- Structured `.pptx` template file with branded slide master
- Dual-interface (CLI + Streamlit) from shared `run_pipeline()` core — demonstrates clean separation of concerns

**Defer (v2+):**
- P&L waterfall bridge (slide 6) — high complexity; a grouped bar is an acceptable fallback
- Anomaly detection rules — add after AI narrative baseline is working
- Multi-company comparison, real-time data fetching, PDF export, batch processing, forecasting/projections, interactive dashboards, natural language query interface

### Architecture Approach

The architecture is a linear pipeline with a single orchestrating function `run_pipeline(excel_path)` that all entry points call. The pipeline has five stages — Ingest, Compute, Charts (parallel with Narrative), Narrative, and Assemble — each represented by a dedicated module under a domain directory (`parser/`, `metrics/`, `charts/`, `narrative/`, `deck/`). Data contracts between stages are typed dataclasses (`FinancialData`, `MetricsBundle`, `ChartBundle`, `NarrativeBundle`). Charts are passed as BytesIO buffers (no intermediate disk I/O). The Claude API call happens after metrics are computed and before deck assembly; the narrative module returns a fallback stub if the API key is absent so the pipeline never hard-blocks on AI availability. See `ARCHITECTURE.md` for the full module directory structure and data flow diagram.

**Major components:**
1. `pipeline.py` (Orchestrator) — the only module both entry points import; sequences all stages; `run_pipeline(excel_path: Path) -> Path`
2. `parser/` (Ingest + Validate) — reads Excel with openpyxl, validates sheet structure and data quality, returns `FinancialData` dataclass
3. `metrics/` (Compute) — all KPI calculations from `FinancialData`; returns `MetricsBundle` dataclass; every downstream stage depends on this
4. `charts/` (Visualization) — matplotlib figures to BytesIO; single `CHART_STYLE` dict for brand consistency; returns `ChartBundle`
5. `narrative/` (AI) — single Claude API call with serialized `MetricsBundle`; parses JSON response; returns `NarrativeBundle` with fallback
6. `deck/` (Assembly) — opens `template.pptx`, places charts + narrative + KPIs onto named placeholders, writes output `.pptx`
7. `generate.py` / `app.py` (Entry Points) — thin wrappers; neither contains business logic

### Critical Pitfalls

1. **Formula cells return None** — openpyxl reads formula results from Excel's cached value store. If the file was never opened and saved in Excel, all formula cells return `None`. Prevention: always use `data_only=True`; add a hard validation gate after parse that checks all required line items are non-null before continuing. This must be solved in Phase 1 or everything downstream is corrupted.

2. **python-pptx placeholder indices are positional, not named** — hardcoded layout indices and placeholder indices break when the template file changes. Prevention: look up layouts by name (`next(l for l in prs.slide_layouts if l.name == "...")`), access placeholders by `idx` constant (not list position), write a `verify_template()` function that validates the template at startup.

3. **Matplotlib charts embedded at low DPI appear blurry** — default matplotlib DPI (100) looks fine on screen but blurs on a projected presentation. Prevention: save all charts at 150-200 DPI (`fig.savefig(buf, dpi=150, bbox_inches='tight')`), use `Inches()` and `prs.slide_width` for EMU-correct sizing.

4. **LLM prompt produces generic text instead of consulting language** — without explicit instruction, Claude defaults to descriptive reporting ("Revenue was $X") not insight-first analysis ("Revenue grew 15% — cloud mix shift the primary driver"). Prevention: system prompt must specify the consulting persona, require insight-first titles, include a one-shot formatting example, and request structured JSON output (title + bullets array per slide).

5. **Streamlit UploadedFile is not a filesystem path** — `st.file_uploader()` returns a BytesIO-like object, not a path string. Passing it to `openpyxl.load_workbook(path)` fails with a type error. Prevention: core parser must accept `Union[str, BinaryIO]`; store generated PPTX bytes in `st.session_state` to survive reruns; gate generation behind a button click to prevent multiple LLM calls.

---

## Implications for Roadmap

Based on the dependency structure in ARCHITECTURE.md and the feature priorities in FEATURES.md, the pipeline's hard dependencies directly dictate phase ordering. Nothing works without parsed, validated financial data. Charts and narrative both depend on computed metrics but are independent of each other. Deck assembly is the integration point. Entry points are a thin wrapper on top of a completed pipeline.

### Phase 1: Excel Ingestion and Validation Foundation

**Rationale:** `FinancialData` is the root dataclass that every other phase depends on. There is no parallelism possible until this stage exists. The formula-cell pitfall (Pitfall 1) and merged-cell pitfall (Pitfall 7) are both Phase 1 concerns that will corrupt all downstream work if unresolved here.

**Delivers:** `parser/ingest.py`, `parser/validate.py`, `parser/models.py` (FinancialData), `data/demo.xlsx`, input template documentation, comprehensive validation error messages

**Addresses features:** Excel parsing with validation, demo data file, documented input template schema, CLI foundation via argparse

**Avoids pitfalls:** Formula cells returning None (use `data_only=True` + validation gate), merged cell misalignment (detect/prohibit in template), row label naming variations (LABEL_ALIASES dict + fuzzy matching), sign convention errors (assert positive revenue)

**Research flag:** Standard — openpyxl parsing patterns are well-documented. No phase research needed.

---

### Phase 2: Metrics Engine

**Rationale:** `MetricsBundle` is the second dependency that all downstream stages (charts AND narrative) require. This phase is pure pandas computation — the most testable and well-defined phase. Unit tests for known financial values belong here and directly support portfolio credibility.

**Delivers:** `metrics/compute.py`, `metrics/models.py` (MetricsBundle), pytest unit tests for all 9+ KPIs with known-value assertions

**Addresses features:** Revenue growth %, gross/EBITDA/net margins, current ratio, D/E, working capital, cash conversion, ROE, ROA

**Avoids pitfalls:** Sign convention errors in EBITDA margin (compute from Operating Income + D&A), test-verified metric correctness

**Research flag:** Standard — pandas arithmetic is well-documented. No phase research needed.

---

### Phase 3: Chart Generation

**Rationale:** Charts are the primary visual output that interviewers screenshot. They depend on MetricsBundle (Phase 2) and must be complete before deck assembly. The waterfall chart implementation (matplotlib stacked-bar technique) is the highest-complexity chart and should be built here so a late-stage refactor is not needed.

**Delivers:** `charts/generate.py`, `charts/style.py` (single CHART_STYLE dict with brand constants), all chart types: clustered bar, line overlay, stacked bar, waterfall

**Addresses features:** Revenue trend chart, margin trend charts, balance sheet composition chart, cash flow waterfall, FCF bridge

**Avoids pitfalls:** Blurry charts (150+ DPI, BytesIO, bbox_inches='tight'), waterfall not in python-pptx (matplotlib stacked-bar from day one), inconsistent brand colors (single rcParams-applied CHART_STYLE)

**Research flag:** Standard for bar/line charts. Waterfall stacked-bar technique is a known pattern — no additional research needed, but implementation requires careful testing.

---

### Phase 4: Deck Assembly and Template

**Rationale:** Assembly integrates ChartBundle and (at this phase) placeholder narrative. Building the layout with stub text first proves the template geometry before the Claude integration adds a variable. The template `.pptx` file is created here and committed — never modified casually after this point.

**Delivers:** `deck/template.pptx` (Big 4 branded master with named layouts and placeholders), `deck/assemble.py`, `deck/slide_defs.py`, `verify_template()` validation function, complete 12-15 slide deck rendering with placeholder narrative

**Addresses features:** All slide types (title, exec summary, section dividers, content slides, scorecard, appendix), consistent color theme, slide numbers and footer, slide master

**Avoids pitfalls:** Layout index brittleness (name-based lookup + verify_template()), font embedding issues (use Calibri/Arial), chart sizing (EMU-correct positioning using Inches() and prs.slide_width)

**Research flag:** Standard — python-pptx assembly patterns are well-documented. Verify python-pptx v1.0 placeholder API in official docs before coding.

---

### Phase 5: AI Narrative Integration

**Rationale:** Claude integration is slotted into the already-verified deck structure from Phase 4. The prompt engineering is the creative and technically risky work; building it after the deck structure is proven means failures are isolated to the narrative module only. Graceful fallback (placeholder text on API error) must be implemented here.

**Delivers:** `narrative/claude.py`, `narrative/models.py` (NarrativeBundle), system prompt with consulting persona and one-shot example, JSON output schema, fallback stub behavior, LLM response validator

**Addresses features:** AI-generated insight-first slide titles, AI narrative bullets (consulting voice), anomaly flag detection passed as prompt context

**Avoids pitfalls:** Generic non-consulting language (explicit persona + insight-first instruction + one-shot example), JSON wrapped in code fences (strip markdown fences before json.loads()), token limits (concise output schema: title + 2-3 bullets ≤ 15 words each), slide count mismatch (validate response completeness; pad with placeholder if below minimum)

**Research flag:** Needs attention — verify current claude-sonnet model ID (may have changed since research cutoff August 2025), check latest anthropic SDK version and token counting API. Prompt iteration will require test runs against demo data.

---

### Phase 6: Entry Points, Pipeline Wire-Up, and Polish

**Rationale:** Entry points are thin wrappers that call `run_pipeline()`. Building them last means the core pipeline is fully verified before exposing it to UI concerns. The Streamlit-specific pitfalls (UploadedFile type, BytesIO reset, session_state caching) are isolated here and not allowed to pollute core modules.

**Delivers:** `pipeline.py` (orchestrator), `generate.py` (CLI), `app.py` (Streamlit UI with spinner, button-gated generation, session_state caching), README with setup/usage/template format/architecture decisions, end-to-end integration test against demo.xlsx

**Addresses features:** CLI interface, Streamlit web UI, README documentation, full pipeline integration

**Avoids pitfalls:** UploadedFile is not a path (parser accepts Union[str, BinaryIO]), BytesIO not reset before download (buf.seek(0) after prs.save()), multiple LLM calls on rerun (button-gated, session_state cache), temp file disappears mid-processing (never write intermediate temp files; pass BytesIO throughout)

**Research flag:** Standard for CLI. Streamlit patterns are well-documented. Verify st.download_button signature against current Streamlit docs (actively versioned).

---

### Phase Ordering Rationale

- **Dependency chain drives order**: FinancialData (Phase 1) → MetricsBundle (Phase 2) → ChartBundle (Phase 3) and NarrativeBundle (Phase 5) → Deck assembly (Phase 4) → Entry points (Phase 6). This is not arbitrary — skipping any phase breaks the next.
- **Charts before narrative in deck**: Phase 4 builds the deck shell with placeholder text so layout geometry is proven before the Claude API is integrated. This isolates prompt engineering failures from layout failures.
- **AI late in pipeline**: Narrative depends only on MetricsBundle, not on charts. Placing it in Phase 5 means API costs are only incurred when the rest of the pipeline is verified working.
- **Entry points last**: No business logic belongs in entry points. Building them last enforces this constraint and prevents logic leaking into UI layers.
- **Tests accompany each phase**: Metric unit tests in Phase 2, chart visual inspection in Phase 3, template verification function in Phase 4, LLM response validation in Phase 5.

### Research Flags

Phases likely needing deeper research or verification during planning:
- **Phase 5 (AI Narrative):** Verify current claude-sonnet model ID and anthropic SDK version before coding. Prompt engineering for consulting voice will require iteration against real data. Check SDK's structured output / tool-use feature as an alternative to regex-based JSON fence stripping.
- **Phase 4 (Deck Assembly):** Verify python-pptx v1.0 API migration notes — v1.0 was released in 2024 and may have changed from 0.x patterns documented in most training examples.

Phases with standard, well-documented patterns (skip research-phase):
- **Phase 1 (Excel Parsing):** openpyxl patterns are stable and extensively documented.
- **Phase 2 (Metrics):** pandas arithmetic is foundational and well-documented.
- **Phase 3 (Charts):** matplotlib-to-BytesIO embedding is a standard pattern; waterfall stacked-bar technique is known.
- **Phase 6 (Entry Points):** argparse is stdlib; Streamlit file upload/download patterns are well-documented.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Core libraries (openpyxl, pandas, matplotlib, argparse) are HIGH confidence — stable, dominant. python-pptx v1.0 API is MEDIUM — released 2024, verify migration from 0.x. anthropic SDK is LOW-MEDIUM — actively versioned, verify before pinning. |
| Features | HIGH | Big 4 deck conventions and financial metric definitions are stable domain knowledge. Portfolio signal for Big 4 interviews is MEDIUM — based on published JDs and interview prep content, not verified against 2026 hiring criteria. |
| Architecture | HIGH | Linear pipeline pattern is the established approach for this class of tool. All official library docs (python-pptx, Streamlit, Anthropic, pandas, matplotlib) confirm the integration patterns described. |
| Pitfalls | MEDIUM | Well-established library behaviors (openpyxl formula caching, python-pptx placeholder indexing, Streamlit rerun model, Claude JSON wrapping). All are consistent with multiple documented sources. Validate against current official docs before treating as authoritative. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **anthropic SDK version and model ID**: Training data cutoff August 2025; a newer claude-sonnet model may be available as of March 2026. Verify the exact current model ID and SDK version before Phase 5 coding. Run `pip index versions anthropic` and check the Anthropic documentation for current model names.
- **python-pptx v1.0 migration**: v1.0 was released in 2024 and the API changed from 0.x. Before Phase 4, read the official migration notes at python-pptx.readthedocs.io to identify any breaking changes in placeholder access or presentation initialization.
- **Waterfall chart implementation**: The stacked-bar waterfall technique is described but not prototyped. Allocate time in Phase 3 for implementation iteration — this is the highest-complexity chart and should not be left to the end of that phase.
- **Competitive tool landscape**: Beautiful.ai, Gamma.app, Tome, and similar AI deck tools were not verifiably surveyed (web search unavailable). The differentiator positioning is based on Big 4 consulting conventions, not confirmed competitive gap analysis.
- **Demo data selection**: Apple or Microsoft annual report data is recommended but the specific year range (e.g., FY2021-FY2025) and exact line item labels need to be confirmed before the demo Excel file is built, since the parser's LABEL_ALIASES must match whatever label conventions the chosen data source uses.

---

## Sources

### Primary (HIGH confidence)
- Official python-pptx documentation: https://python-pptx.readthedocs.io/
- Official Streamlit documentation: https://docs.streamlit.io/
- Official Anthropic API documentation: https://docs.anthropic.com/
- Official pandas documentation: https://pandas.pydata.org/docs/
- Official matplotlib documentation: https://matplotlib.org/stable/

### Secondary (MEDIUM confidence)
- Training data: Big 4 consulting deck conventions (Deloitte, McKinsey, PwC publicly available frameworks)
- Training data: Financial analysis curriculum (CFA, MBA) for metric definitions and sign conventions
- Training data: openpyxl documented behaviors (data_only mode, merged cells, formula caching) — validate against https://openpyxl.readthedocs.io/en/stable/
- Training data: Consulting interview prep content for portfolio project evaluation criteria

### Tertiary (LOW confidence)
- Competitive tool landscape (Beautiful.ai, Gamma.app, Tome) — web search unavailable; feature comparison not verified against current 2026 state
- Portfolio signal for Big 4 tech consulting interviews — based on published job descriptions from training data, not verified against 2026 hiring criteria

---
*Research completed: 2026-03-09*
*Ready for roadmap: yes*

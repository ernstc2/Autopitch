# Architecture Patterns

**Project:** Autopitch
**Domain:** Python CLI/Web tool — Excel financial data → PowerPoint deck + AI narrative
**Researched:** 2026-03-09
**Confidence:** HIGH (well-established Python tooling; patterns drawn from python-pptx, pandas, Streamlit ecosystem)

---

## Recommended Architecture

The system is a **linear transformation pipeline** with two entry points (CLI and Streamlit UI) that converge on a shared pipeline core. The Claude API sits in the assembly stage, not the charting stage — it consumes computed metrics and produces narrative text that gets injected into slides.

```
┌─────────────────────────────────────────────────────────────────┐
│                        ENTRY POINTS                             │
│                                                                 │
│   CLI: generate.py financials.xlsx     Streamlit: app.py        │
│         (ArgumentParser)               (file_uploader widget)   │
└───────────────────────┬────────────────────────┬────────────────┘
                        │                        │
                        └──────────┬─────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                     PIPELINE CORE (pipeline.py)                  │
│                                                                  │
│  run_pipeline(excel_path: Path) -> Path (output .pptx path)      │
└────┬─────────────────┬──────────────────┬────────────────────────┘
     │                 │                  │
     ▼                 ▼                  ▼
┌─────────┐    ┌──────────────┐    ┌────────────────┐
│ INGEST  │    │   COMPUTE    │    │    NARRATIVE   │
│         │───▶│              │───▶│  (Claude API)  │
│ parser/ │    │  metrics/    │    │                │
│         │    │              │    │  narrative/    │
└─────────┘    └──────┬───────┘    └───────┬────────┘
                      │                    │
                      ▼                    │
               ┌────────────┐              │
               │   CHARTS   │              │
               │            │              │
               │  charts/   │              │
               └─────┬──────┘              │
                     │                     │
                     └──────────┬──────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    DECK ASSEMBLY      │
                    │                       │
                    │    deck/              │
                    └───────────┬───────────┘
                                │
                                ▼
                         output/deck.pptx
```

---

## Component Boundaries

| Component | Module Path | Responsibility | Inputs | Outputs |
|-----------|-------------|---------------|--------|---------|
| **CLI Entry** | `generate.py` | Parse argv, call pipeline, print result path | `sys.argv` | Calls `run_pipeline()` |
| **Streamlit UI** | `app.py` | File upload widget, progress display, download button | Browser file upload | Calls `run_pipeline()`, serves `.pptx` |
| **Pipeline Orchestrator** | `pipeline.py` | Wire all stages in sequence; single callable for both UIs | `excel_path: Path` | `output_path: Path` |
| **Ingest / Parser** | `parser/ingest.py` | Read Excel, validate sheet names, validate column structure, return typed DataFrames | `Path` to `.xlsx` | `FinancialData` dataclass |
| **Validation** | `parser/validate.py` | Check required sheets exist, required columns present, data types correct, flag anomalies | `FinancialData` | `ValidationResult` (errors list + warnings list) |
| **Metrics Engine** | `metrics/compute.py` | Compute all derived KPIs from raw DataFrames | `FinancialData` | `MetricsBundle` dataclass |
| **Chart Generator** | `charts/generate.py` | Produce matplotlib figures for each section; return as in-memory `BytesIO` PNG buffers | `MetricsBundle` | `ChartBundle` (dict of `BytesIO`) |
| **Narrative Generator** | `narrative/claude.py` | Build structured prompt from `MetricsBundle`, call Claude API, parse response into per-section narrative dicts | `MetricsBundle` | `NarrativeBundle` (dict of slide titles + bullets) |
| **Deck Assembler** | `deck/assemble.py` | Take template `.pptx`, place charts, narrative, and data onto slide layouts; write output | `ChartBundle + NarrativeBundle + MetricsBundle` | `.pptx` file on disk |
| **Template** | `deck/template.pptx` | Master slide layout with Big 4 styling (color theme, fonts, placeholder positions) | — | — |
| **Demo Data** | `data/demo.xlsx` | Pre-built Apple or MSFT financials in the required format | — | — |

---

## Data Flow

```
Excel File (.xlsx)
  │
  ▼
[parser/ingest.py]
  Reads 3 sheets (P&L, Balance Sheet, Cash Flow)
  Validates structure
  Returns: FinancialData
    ├── pl: pd.DataFrame          (revenue, COGS, EBITDA, net income by period)
    ├── bs: pd.DataFrame          (assets, liabilities, equity by period)
    └── cf: pd.DataFrame          (operating, investing, financing CF by period)
  │
  ▼
[metrics/compute.py]
  Returns: MetricsBundle
    ├── revenue_growth: list[float]
    ├── gross_margin: list[float]
    ├── ebitda_margin: list[float]
    ├── net_margin: list[float]
    ├── working_capital: list[float]
    ├── current_ratio: list[float]
    ├── de_ratio: list[float]
    ├── cash_conversion: list[float]
    ├── roe: list[float]
    ├── roa: list[float]
    └── periods: list[str]         (FY2021, FY2022, FY2023...)
  │
  ├─────────────────────┐
  ▼                     ▼
[charts/generate.py]   [narrative/claude.py]
  Returns:               Returns:
  ChartBundle            NarrativeBundle
  (BytesIO PNGs)         (per-section titles + bullets)
  │                     │
  └──────────┬──────────┘
             ▼
[deck/assemble.py]
  Opens deck/template.pptx
  For each slide definition:
    - Fills title placeholder (from NarrativeBundle)
    - Inserts chart image (from ChartBundle)
    - Fills bullet placeholders (from NarrativeBundle)
    - Fills KPI callouts (from MetricsBundle)
  Writes: output/[company]_deck.pptx
             │
             ▼
     Return path to entry point (CLI prints it, Streamlit offers download)
```

---

## Suggested Build Order

The pipeline has hard dependencies — each stage can only be built after its upstream component. This directly maps to phase ordering.

```
Phase 1: Ingest + Validation
  → parser/ingest.py, parser/validate.py
  → FinancialData dataclass defined here; everything downstream depends on it
  → Demo Excel file created alongside (validates the parser works on real data)

Phase 2: Metrics Engine
  → metrics/compute.py
  → Requires FinancialData from Phase 1
  → MetricsBundle dataclass defined here; charts and narrative both depend on it

Phase 3: Chart Generation
  → charts/generate.py
  → Requires MetricsBundle from Phase 2
  → Can be developed/tested independently of narrative

Phase 4: Deck Assembly (layout only, placeholder narrative)
  → deck/template.pptx creation, deck/assemble.py
  → Requires ChartBundle from Phase 3
  → Build with hardcoded/placeholder text first; proves layout before Claude integration

Phase 5: AI Narrative (Claude API)
  → narrative/claude.py
  → Requires MetricsBundle from Phase 2
  → Can be slotted into the already-assembled deck structure from Phase 4
  → One API call per pipeline run; fallback to placeholder text if key missing

Phase 6: CLI + Streamlit UI
  → generate.py (CLI), app.py (Streamlit)
  → Both require pipeline.py (the orchestrator) which wraps Phases 1-5
  → Build CLI first (single function call); Streamlit is a thin wrapper on top
  → pipeline.py is the only module both entry points import
```

---

## How CLI and Streamlit UI Share the Same Core Pipeline

Both entry points call one function:

```python
# pipeline.py
def run_pipeline(excel_path: Path, output_dir: Path = Path("output")) -> Path:
    data = ingest(excel_path)
    validate(data)                    # raises ValidationError on hard failures
    metrics = compute_metrics(data)
    charts = generate_charts(metrics)
    narrative = generate_narrative(metrics)
    output_path = assemble_deck(charts, narrative, metrics, output_dir)
    return output_path
```

```python
# generate.py (CLI)
if __name__ == "__main__":
    path = run_pipeline(Path(sys.argv[1]))
    print(f"Deck saved to: {path}")
```

```python
# app.py (Streamlit)
uploaded = st.file_uploader("Upload Excel", type="xlsx")
if uploaded:
    tmp = save_to_temp(uploaded)
    output_path = run_pipeline(tmp)
    st.download_button("Download Deck", open(output_path, "rb"), file_name="deck.pptx")
```

This means: **all logic lives in pipeline.py and its sub-modules**. Neither entry point contains business logic. Changing the pipeline does not touch the UI layer. Testing `run_pipeline()` directly validates the full chain.

---

## How Claude API Fits Into the Assembly Pipeline

Claude is called **after metrics are computed and before deck assembly**, giving it all numerical context it needs to write meaningful commentary.

```
MetricsBundle
  │
  ▼
[narrative/claude.py]
  1. Serialize MetricsBundle to structured context dict
  2. Build prompt:
     - System: "You are a management consultant writing slide content..."
     - User: JSON block of all metrics + periods + company name
     - Request: JSON output with keys for each slide section
       { "overview_title": "...", "overview_bullets": [...], ... }
  3. Call Claude API (claude-sonnet model, single call per deck)
  4. Parse JSON response → NarrativeBundle dataclass
  5. On API error or missing key: return NarrativeBundle with placeholder text
     (deck assembly never blocks on narrative failure)
  │
  ▼
NarrativeBundle fed into deck/assemble.py
```

Key design decision: **one API call per deck run** (not per slide). The full metrics context is passed in a single structured prompt, and Claude returns all slide narratives in a single JSON response. This keeps latency low, cost minimal, and makes the prompt inspectable.

The `ANTHROPIC_API_KEY` env var check happens at module import time in `narrative/claude.py`. If absent, the module logs a warning and returns a stub `NarrativeBundle` so the rest of the pipeline completes — the deck renders with placeholder text instead of AI commentary.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Putting Logic in Entry Points
**What:** Writing metric computation or slide assembly code directly in `generate.py` or `app.py`.
**Why bad:** Duplicates logic across entry points; breaks when you add a third entry point; impossible to unit test without invoking the UI.
**Instead:** All logic in `pipeline.py` and sub-modules. Entry points are < 30 lines each.

### Anti-Pattern 2: One-Call-Per-Slide to Claude
**What:** Making a separate Claude API call for each slide section (12-15 calls per deck run).
**Why bad:** 10-30 seconds of latency; 15x the cost; rate limiting risk; complex error handling across 15 calls.
**Instead:** Single call with all metrics serialized as JSON; Claude returns all narratives in one structured response.

### Anti-Pattern 3: Embedding Charts as File Paths
**What:** Writing chart PNG files to disk, passing file paths to the assembler.
**Why bad:** Creates temp file management complexity; fails in read-only environments (Streamlit Cloud); requires cleanup logic.
**Instead:** Pass `BytesIO` buffers directly from chart generator to assembler. No disk I/O for intermediate artifacts.

### Anti-Pattern 4: Hardcoding Slide Structure in Assembler
**What:** Building slide content with magic indices (`slide.placeholders[2]`).
**Why bad:** Fragile to template changes; impossible to reason about without opening the PPTX.
**Instead:** Use named placeholder tags in the template (`ph_title`, `ph_subtitle`, `ph_chart_1`). Access by `ph.name` in assembler code.

### Anti-Pattern 5: Tight Coupling Between Metrics and Chart Style
**What:** Chart generator imports from metrics module and also decides colors/styles.
**Why bad:** Changing styling requires touching metrics logic; impossible to restyle without understanding metric computation.
**Instead:** Chart generator accepts only data (lists/dicts from MetricsBundle). All styling lives in `charts/style.py` as constants.

---

## Module Directory Structure

```
autopitch/
├── generate.py          # CLI entry point
├── app.py               # Streamlit entry point
├── pipeline.py          # Orchestrator — the only module both entry points import
│
├── parser/
│   ├── __init__.py
│   ├── ingest.py        # Excel reading, DataFrame construction
│   ├── validate.py      # Schema and data quality checks
│   └── models.py        # FinancialData dataclass
│
├── metrics/
│   ├── __init__.py
│   ├── compute.py       # All KPI calculations
│   └── models.py        # MetricsBundle dataclass
│
├── charts/
│   ├── __init__.py
│   ├── generate.py      # Chart figure creation → BytesIO
│   └── style.py         # Color palette, font sizes, Big 4 aesthetic constants
│
├── narrative/
│   ├── __init__.py
│   ├── claude.py        # Claude API call, prompt construction, response parsing
│   └── models.py        # NarrativeBundle dataclass
│
├── deck/
│   ├── __init__.py
│   ├── assemble.py      # python-pptx assembly logic
│   ├── template.pptx    # Master slide template
│   └── slide_defs.py    # Declarative slide structure (slide type, content mappings)
│
├── data/
│   └── demo.xlsx        # Apple or MSFT public financials in required format
│
└── output/              # Generated decks written here (gitignored)
```

---

## Scalability Considerations

This is a stateless single-run tool, so traditional scalability concerns do not apply. The relevant axes are:

| Concern | Current (v1) | If Demonstrated in Portfolio Demo |
|---------|--------------|----------------------------------|
| Multiple companies | Not in scope | Add `company_name` param to `run_pipeline()`; no structural change needed |
| Concurrent Streamlit users | Single-user local/demo | Streamlit handles concurrency via session state; pipeline is stateless so concurrent calls are safe |
| Multiple Claude models | `claude-sonnet` hardcoded | Move model name to config constant in `narrative/claude.py` |
| Custom templates | One template | `template_path` param to `run_pipeline()`; assembler already takes path |

---

## Sources

- python-pptx documentation: https://python-pptx.readthedocs.io/ (HIGH confidence — official docs)
- Streamlit file upload + download patterns: https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader (HIGH confidence — official docs)
- Anthropic Claude API (structured JSON output, single-call patterns): https://docs.anthropic.com/en/api/getting-started (HIGH confidence — official docs)
- pandas DataFrame patterns for financial data: https://pandas.pydata.org/docs/ (HIGH confidence — official docs)
- matplotlib BytesIO figure export: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html (HIGH confidence — official docs)
- Architecture patterns: based on well-established Python pipeline conventions (training data, HIGH confidence for this class of tool)

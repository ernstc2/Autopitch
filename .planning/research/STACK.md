# Technology Stack

**Project:** Autopitch — Python financial deck generator (Excel -> PowerPoint + AI narrative)
**Researched:** 2026-03-09
**Research mode:** Training knowledge only (WebSearch, WebFetch, and Bash blocked in this environment)

> **VERSION WARNING:** All version numbers below are derived from training data (cutoff August 2025).
> Before coding, run `pip index versions <package>` or check PyPI for the true latest.
> Pinned versions in `requirements.txt` should be set only after manual verification.

---

## Recommended Stack

### Excel Parsing

| Technology | Version (verify) | Purpose | Why |
|------------|-----------------|---------|-----|
| openpyxl | ^3.1 | Read multi-sheet `.xlsx` workbooks | Pure-Python, no Excel dependency, full cell/formula/named-range access, sheet iteration, data type preservation. The standard for structural workbook reading in 2025. |
| pandas | ^2.2 | DataFrame representation of parsed sheet data | Vectorized column operations, built-in `.pct_change()` / `.rolling()`, cleaner metric computation than raw openpyxl row loops. |

**openpyxl vs pandas direct Excel read:** Use openpyxl for the structural read (sheet discovery, header detection, cell-level validation) and hand data off to pandas DataFrames for computation. Do not use `pd.read_excel()` as the primary parser — it silently drops formatting context needed for column mapping and skips validation opportunities.

**Why not xlrd:** Dropped `.xlsx` support in v2.0 (2020). `.xls`-only now. Dead end.
**Why not xlwings:** Requires a live Excel installation. Non-starter on CI/servers.

---

### Financial Computation

| Technology | Version (verify) | Purpose | Why |
|------------|-----------------|---------|-----|
| pandas | ^2.2 | Metric computation (growth rates, margins, ratios) | Already in stack for data representation. `.pct_change()`, `.div()`, boolean masking cover all required metrics without additional dependencies. |
| numpy | ^1.26 (pandas dependency) | Underlying array math | Pulled in by pandas automatically. Use `numpy.nan` for missing-value handling in ratio computations. |

**No need for:** `scipy`, `statsmodels`, or any ML library. The required metrics (revenue growth, EBITDA margin, D/E ratio, current ratio, cash conversion, ROE, ROA) are straightforward arithmetic on labeled columns. Adding heavier libraries would signal over-engineering to reviewers.

---

### Chart Generation

| Technology | Version (verify) | Purpose | Why |
|------------|-----------------|---------|-----|
| matplotlib | ^3.9 | Bar charts, line charts, waterfall charts embedded in PPTX | Outputs to BytesIO in-memory PNG/SVG; python-pptx accepts BytesIO directly via `add_picture()`. Fine-grained style control needed for Big 4 color palette (navy/teal, no chart borders, minimal gridlines). |

**matplotlib vs plotly:** Plotly produces interactive HTML charts. python-pptx cannot embed Plotly output directly — it requires a headless browser render step (kaleido) or screenshot, adding a fragile dependency. Matplotlib renders directly to bytes in-process. For a static PPTX deliverable, matplotlib is the correct choice.

**matplotlib vs chart shapes native to PPTX:** `python-pptx` has a native chart API (`prs.slides[i].shapes.add_chart()`). Avoid it for this project: the native chart XML is limited (no waterfall chart type), styling is verbose and brittle, and the output looks like a default Office chart. Matplotlib-rendered images give precise Big 4 aesthetic control.

**Waterfall charts:** matplotlib has no built-in waterfall. Use a stacked bar trick (invisible base bar + visible delta bar) or the `waterfall_chart` third-party package (^0.2). Verify whether `waterfall_chart` is still maintained before use — if not, implement the stacked-bar approach manually (it's ~30 lines and has no external dependency).

---

### PowerPoint Generation

| Technology | Version (verify) | Purpose | Why |
|------------|-----------------|---------|-----|
| python-pptx | ^1.0 | Build `.pptx` file structure, add slides, text boxes, image placeholders | The only maintained pure-Python PPTX library. v1.0 (released 2024) introduced a cleaner API. Directly controls EMU-level positioning needed for precise Big 4 layout. |

**Why not LibreOffice / COM automation:** Requires installed Office suite, non-portable, not suitable for a portfolio tool that should run anywhere.

**Slide layout strategy:** Do not use the default slide layouts from a blank presentation — they are ugly Office defaults. Define a custom `.pptx` template file (committed to the repo) with pre-configured masters: title slide, section divider, content slide (chart left, bullets right), full-bleed chart slide. Load via `Presentation('template.pptx')`. This approach is the correct python-pptx pattern and avoids reimplementing slide geometry in code.

---

### AI Narrative Generation

| Technology | Version (verify) | Purpose | Why |
|------------|-----------------|---------|-----|
| anthropic | ^0.28 (verify — actively versioned) | Python SDK for Claude API calls | Official SDK from Anthropic. Handles auth, retry, streaming. Use `claude-sonnet-4-5` or latest available `claude-sonnet` model — balances quality and cost. The PROJECT.md specifies Claude; this is a project constraint not a choice. |

**API call strategy:** One call per deck with a structured JSON context block containing all computed metrics and growth rates. Do not call per-slide — it multiplies cost and creates tonal inconsistency. Design a single prompt that returns a JSON object keyed by slide section (e.g., `{"revenue": {"title": "...", "bullets": ["...", "..."]}, "margins": {...}}`). Parse and distribute to slides.

**Model selection:** `claude-sonnet-4-5` at research time (August 2025). As of March 2026 a newer Sonnet version may be available — always use the latest `claude-sonnet` model ID available in your account. Avoid Haiku for this use case: financial narrative quality degrades noticeably on shorter models. Avoid Opus: overkill for structured bullet generation and expensive for a demo tool.

**Environment variable:** `ANTHROPIC_API_KEY` loaded via `python-dotenv` (see Supporting Libraries).

---

### Web UI

| Technology | Version (verify) | Purpose | Why |
|------------|-----------------|---------|-----|
| streamlit | ^1.35 | Browser-based file upload and PPTX download | Zero backend infrastructure, Python-native, file upload widget, `st.download_button()` for PPTX delivery. Produces an impressive demo with ~50 lines. The PROJECT.md mandates this. |

**Streamlit vs Gradio:** Both are viable for a demo UI. Streamlit is more widely recognized by tech consulting interviewers, has better layout control for a polished look, and has a larger ecosystem. Gradio is better suited to ML model demos. Streamlit is correct here.

**Statelessness:** Each Streamlit session runs the full pipeline independently. No session state persistence needed beyond the current request lifecycle. Use `st.session_state` only if adding progress display.

---

### CLI Interface

| Technology | Purpose | Why |
|------------|---------|-----|
| argparse (stdlib) | `python generate.py financials.xlsx` CLI | No external dependency. Simple single-argument CLI doesn't need Click or Typer. Stdlib argparse is sufficient and signals clean Python to reviewers. |

**Why not Click/Typer:** Adds a dependency for a CLI with one positional argument. Overkill. If the CLI grows beyond 3-4 flags, migrate to Typer (type-annotated, modern feel) — but do not preemptively add it.

---

### Supporting Libraries

| Library | Version (verify) | Purpose | When to Use |
|---------|-----------------|---------|-------------|
| python-dotenv | ^1.0 | Load `ANTHROPIC_API_KEY` from `.env` file | Always — prevents hardcoded credentials, standard pattern |
| Pillow (PIL) | ^10.x (matplotlib dependency) | Image processing for chart byte streams | Pulled in by matplotlib; no direct usage needed |
| pytest | ^8.x | Unit tests for metric computation and data validation | Test layer for financial formula correctness — critical for portfolio credibility |
| pytest-cov | ^5.x | Coverage reporting | Pair with pytest; shows test discipline to reviewers |
| black | ^24.x | Code formatting | Run pre-commit; consulting codebase aesthetics matter |
| ruff | ^0.4 | Linting | Faster than flake8/pylint, single config, 2025 standard |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Excel read | openpyxl + pandas | `pd.read_excel()` only | Loses structural validation, silently skips header rows |
| Excel read | openpyxl + pandas | xlrd | Dropped .xlsx support in 2020; dead end |
| Excel read | openpyxl + pandas | xlwings | Requires live Excel installation |
| Charts | matplotlib (to image) | python-pptx native charts | No waterfall type; ugly defaults; verbose styling |
| Charts | matplotlib (to image) | plotly + kaleido | Headless browser dependency; fragile; slower |
| CLI | argparse | Click / Typer | Unnecessary dependency for single-argument CLI |
| AI | anthropic SDK | openai SDK + GPT-4o | Project constraint specifies Claude; also: Claude's structured output quality for financial narrative is strong |
| Formatting | black + ruff | flake8 + isort | ruff replaces both flake8 and isort in one tool; 2025 standard |

---

## Python Version

Use Python **3.11** or **3.12**.

- 3.11: Significant performance improvements over 3.10; stable; widely available in CI.
- 3.12: Even faster, better error messages, available since Oct 2023; good choice if your environment supports it.
- Avoid 3.13 (alpha/RC status as of research cutoff; ecosystem compatibility not confirmed).

Pin in `.python-version` for reproducibility.

---

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Core runtime
pip install openpyxl pandas matplotlib python-pptx anthropic streamlit python-dotenv

# Dev dependencies
pip install pytest pytest-cov black ruff

# Optional (if implementing waterfall chart via package instead of manual)
# pip install waterfall_chart  # verify maintenance status before using
```

Freeze after installation:
```bash
pip freeze > requirements.txt
```

Recommended `requirements.txt` structure (split runtime vs dev):
```
# requirements.txt — runtime
openpyxl>=3.1,<4.0
pandas>=2.2,<3.0
matplotlib>=3.9,<4.0
python-pptx>=1.0,<2.0
anthropic>=0.28,<1.0
streamlit>=1.35,<2.0
python-dotenv>=1.0,<2.0

# requirements-dev.txt — development only
pytest>=8.0,<9.0
pytest-cov>=5.0,<6.0
black>=24.0,<25.0
ruff>=0.4,<1.0
```

---

## Confidence Assessment

| Library | Confidence | Reason |
|---------|------------|--------|
| openpyxl | HIGH | Stable, dominant library for years; no competitor emerged |
| pandas | HIGH | Foundational; version 2.x is well-established |
| matplotlib | HIGH | Correct choice for static image embedding; well-understood |
| python-pptx | MEDIUM | v1.0 released in 2024 — API may have changed from 0.x; verify migration notes |
| anthropic SDK | LOW-MEDIUM | Actively developed; version number changes rapidly; verify latest before pinning |
| streamlit | MEDIUM | Actively developed; minor API changes between minor versions; verify `st.download_button` signature |
| argparse | HIGH | Stdlib; no version concern |
| python-dotenv | HIGH | Stable, minimal library; no churn |

---

## Sources

- Training knowledge (cutoff August 2025) — all findings
- Project constraints from `.planning/PROJECT.md` (openpyxl/pandas, python-pptx, matplotlib/plotly, Streamlit explicitly listed as constraints)
- Version numbers require verification via `pip index versions <package>` or https://pypi.org before pinning

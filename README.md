# Autopitch

Turn a single Excel file of financial data into a boardroom-ready consulting deck in seconds.

---

## Overview

Autopitch is a Python tool that reads a three-sheet Excel workbook (P&L, Balance Sheet, Cash Flow) and outputs a polished PowerPoint pitch deck styled after Big 4 consulting firms — navy and teal palette, Calibri typography, properly scaled charts on every slide.

The pipeline runs in five stages: parse the workbook, compute financial metrics, generate AI-written insight-first slide titles and commentary via the Claude API, assemble the PowerPoint, and deliver the file. The entire pipeline is testable without an API key: when `ANTHROPIC_API_KEY` is absent, every step runs normally and placeholder text fills the commentary blocks — no crash, no error, no degraded output structure.

Output is a 12-slide deck covering KPI summary, revenue and profitability trends, balance sheet health, and cash flow analysis — the kind of deck that would take a financial analyst two or more hours to build manually.

---

## Quick Start

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/autopitch.git
   cd autopitch
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Configure your API key (optional — see [Configuration](#configuration)):

   ```
   cp .env.example .env
   # Open .env and paste your Anthropic API key
   ```

4. Generate a deck from the included demo data:

   ```
   python generate.py demo/apple_financials.xlsx
   ```

5. Open the output file:

   ```
   open apple_financials.pptx   # macOS
   start apple_financials.pptx  # Windows
   ```

---

## Installation

Requires Python 3.11 or later.

```
pip install -r requirements.txt
```

Key dependencies: `python-pptx`, `openpyxl`, `matplotlib`, `pydantic`, `anthropic`, `streamlit`, `python-dotenv`.

---

## Configuration

### API Key

Autopitch uses the Claude API to generate insight-first slide titles and bullet-point commentary. To enable AI-generated narrative:

1. Copy the example environment file:

   ```
   cp .env.example .env
   ```

2. Open `.env` and paste your Anthropic API key:

   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. Get an API key at [console.anthropic.com](https://console.anthropic.com).

**Without an API key:** The tool still generates a complete, fully-formatted deck. Slide titles and commentary blocks display placeholder text instead of AI-generated content. All charts, metrics, and layout are identical — only the narrative text differs. This means you can run the full test suite and demo without any API credentials.

---

## Usage: CLI

Run the CLI entry point with a path to your Excel workbook:

```
python generate.py demo/apple_financials.xlsx
```

The default output file is `<input_stem>.pptx` written to the current directory. For the demo file, this produces `apple_financials.pptx`.

To specify a custom output path, use the `-o` flag:

```
python generate.py demo/apple_financials.xlsx -o output/my_deck.pptx
```

If the workbook fails validation (missing sheets, missing required rows, invalid values), the CLI prints the error to stderr and exits with code 1.

---

## Usage: Streamlit

Launch the web UI:

```
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser. Upload an Excel workbook (`.xlsx`), click **Generate Deck**, and download the resulting `.pptx` file directly from the browser.

The Streamlit app and the CLI use identical pipeline logic — both call the same `run_pipeline()` function in `autopitch/pipeline.py`.

---

## Excel Input Format

The workbook must contain exactly three sheets: `P&L`, `Balance Sheet`, and `Cash Flow`. Row 1 of each sheet is the header row with fiscal year labels in the format `FYXXXX` (e.g., `FY2022`, `FY2023`, `FY2024`). All values must be entered as positive numbers.

Full schema — required rows per sheet, sign conventions, multi-year rules, and common pitfalls — is documented in [TEMPLATE_FORMAT.md](TEMPLATE_FORMAT.md).

The included demo file `demo/apple_financials.xlsx` contains Apple's financials for FY2020–FY2024 and is a ready-to-use reference for the expected format.

---

## Architecture

The pipeline is a linear chain of pure functions with no shared state:

```
parse_workbook()
    -> compute_metrics()
    -> generate_narrative()
    -> build_deck()
    -> run_pipeline()  (integration point)
```

`run_pipeline(source)` in `autopitch/pipeline.py` is the single integration point called by both `generate.py` (CLI) and `app.py` (Streamlit). It accepts a file path (`str` or `Path`) or a binary stream (`BinaryIO`) — so the same function handles both entry points without branching. It returns the PPTX as raw bytes.

The `autopitch/` package is a pure library with no I/O coupling. Entry points (`generate.py`, `app.py`) handle all file I/O and UI; the library handles all computation and rendering.

| Module | Role |
|--------|------|
| `autopitch/parser.py` | Read and validate Excel workbook |
| `autopitch/metrics.py` | Compute financial ratios and growth rates |
| `autopitch/narrative.py` | Call Claude API to generate slide narrative |
| `autopitch/deck.py` | Build PowerPoint presentation |
| `autopitch/pipeline.py` | Wire all stages together into one callable |
| `autopitch/theme.py` | Color palette and typography constants |
| `autopitch/models.py` | Pydantic models and ValidationError |
| `generate.py` | CLI entry point |
| `app.py` | Streamlit web UI entry point |

---

## Development and Tests

Run the full test suite:

```
pytest -q
```

Tests run without an API key. The narrative module uses a `NarrativeOutput()` placeholder when `ANTHROPIC_API_KEY` is absent, so all 39+ tests pass in any environment.

To run only the documentation tests:

```
pytest tests/test_docs.py -q
```

Tests are organized by module: `test_parser.py`, `test_validator.py`, `test_metrics.py`, `test_charts.py`, `test_deck.py`, `test_narrative.py`, `test_docs.py`.

# Architecture Research

**Domain:** Streamlit portfolio demo UI — v1.1 integration into existing autopitch pipeline
**Researched:** 2026-03-10
**Confidence:** HIGH (official Streamlit docs verified; existing codebase directly inspected)

---

## Context: What Already Exists

The v1.0 codebase is a working linear pipeline with two thin entry points:

```
generate.py (CLI)          app.py (Streamlit, 38 lines)
        \                       /
         \                     /
          autopitch/pipeline.py
              run_pipeline(source) -> bytes
                    |
          parser -> metrics -> narrative -> deck
```

**Actual module layout (as-shipped):**

```
Autopitch/
├── app.py                    # Streamlit entry point — 38 lines
├── generate.py               # CLI entry point — 50 lines
├── autopitch/
│   ├── pipeline.py           # Orchestrator: run_pipeline(source) -> bytes
│   ├── models.py             # FinancialData, MetricsOutput, ValidationError (Pydantic v2)
│   ├── parser.py             # parse_workbook(source: Union[str, Path, BinaryIO]) -> FinancialData
│   ├── metrics.py            # compute_metrics(data) -> MetricsOutput
│   ├── narrative.py          # generate_narrative(data, metrics) -> NarrativeOutput
│   ├── deck.py               # build_deck(data, metrics, narrative) -> Presentation
│   ├── charts.py             # chart generation helpers
│   ├── theme.py              # Big 4 color palette constants
│   └── validator.py          # validation logic
├── demo/
│   └── apple_financials.xlsx # Bundled demo data
├── requirements.txt          # anthropic, openpyxl, pydantic, streamlit, python-dotenv
└── pyproject.toml
```

**Key signatures confirmed from source:**

- `run_pipeline(source: Union[str, Path, BinaryIO]) -> bytes` — returns PPTX as raw bytes
- `parse_workbook(source)` accepts both file paths and BinaryIO streams
- `generate_narrative()` checks `os.environ.get("ANTHROPIC_API_KEY")` at call time — no import-time failure if key absent
- `NarrativeOutput` is a Pydantic v2 frozen model with placeholder defaults for all fields

---

## What v1.1 Adds to the Architecture

v1.1 is **entirely a UI layer change**. The pipeline core (`autopitch/` package) does not change. All four target features are implemented in `app.py` and new support files.

| Feature | Where It Lives | Pipeline Impact |
|---------|---------------|-----------------|
| Demo-first landing + one-click Apple demo | `app.py` — UI sections | None: calls existing `run_pipeline()` with bundled file bytes |
| Skills/tech showcase section | `app.py` — static display | None: pure Streamlit widgets, no pipeline |
| Downloadable Excel template | `app.py` — `st.download_button` | None: reads `demo/apple_financials.xlsx` or a new `template.xlsx` from disk |
| Streamlit Cloud deployment | `secrets.toml` + Cloud config | Minimal: API key moved from `.env` to `st.secrets`; pipeline code unchanged |
| Polished UI layout | `app.py` — layout restructure | None: visual only |

---

## System Overview: v1.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         STREAMLIT CLOUD                              │
│                     (share.streamlit.io)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   app.py  (expanded: ~120-180 lines)                                 │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  SECTION 1: Hero / Landing                                    │   │
│  │    st.title, st.markdown — tagline, value prop               │   │
│  │    [Try the Demo] button  →  loads demo_bytes into state     │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  SECTION 2: Demo Mode (when demo active)                     │   │
│  │    st.info banner: "Running on Apple FY2020-FY2024 data"     │   │
│  │    [Generate Demo Deck] button                               │   │
│  │      → run_pipeline(BytesIO(demo_bytes))                     │   │
│  │      → st.download_button for PPTX                           │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  SECTION 3: Upload Your Own Data                             │   │
│  │    st.expander or st.tabs                                    │   │
│  │    st.file_uploader (xlsx)                                   │   │
│  │    [Generate Deck] button                                    │   │
│  │      → run_pipeline(uploaded_file)                           │   │
│  │      → st.download_button for PPTX                           │   │
│  │    st.download_button: "Download Excel Template"             │   │
│  │      → reads demo/apple_financials.xlsx bytes                │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │  SECTION 4: Skills / Tech Stack Showcase                     │   │
│  │    st.columns — badge grid                                   │   │
│  │    Static markdown: Python, Pydantic, Claude API, etc.       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   autopitch/ package — UNCHANGED from v1.0                          │
│   ┌──────────────────────────────────────────────────────────────┐  │
│   │  pipeline.py → parser → metrics → narrative → deck           │  │
│   └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
│   Secrets: .streamlit/secrets.toml (local) / Cloud Settings (prod)  │
│   ANTHROPIC_API_KEY = "sk-..."  (root-level → auto env var)         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Responsibilities

### Existing Components (unchanged)

| Component | Module | Responsibility | v1.1 Change |
|-----------|--------|---------------|-------------|
| Pipeline Orchestrator | `autopitch/pipeline.py` | Sequences all stages, returns PPTX bytes | None |
| Parser | `autopitch/parser.py` | Reads Excel, validates, returns FinancialData | None |
| Metrics | `autopitch/metrics.py` | Computes all KPIs, returns MetricsOutput | None |
| Narrative | `autopitch/narrative.py` | Claude API call, returns NarrativeOutput | None (API key source changes — see below) |
| Deck Builder | `autopitch/deck.py` | Assembles PPTX, returns Presentation | None |
| CLI Entry | `generate.py` | argparse → run_pipeline() | None |

### Modified Component

| Component | Module | v1.1 Change | Why |
|-----------|--------|-------------|-----|
| Streamlit UI | `app.py` | Expand from 38 lines to ~150 lines; restructure into 4 sections | Add hero, demo mode, template download, skills section |

### New Components

| Component | Path | Responsibility |
|-----------|------|---------------|
| Secrets config (local) | `.streamlit/secrets.toml` | Holds `ANTHROPIC_API_KEY` for local dev (mirrors Cloud secrets) |
| Gitignore entry | `.gitignore` | Ensure `.streamlit/secrets.toml` is never committed |
| Excel template file | `demo/template.xlsx` (optional) | Clean blank template with correct headers; if not created, `apple_financials.xlsx` doubles as the template download |

---

## Data Flow: One-Click Demo

The demo button must load the bundled Excel file and pass it to `run_pipeline()` without touching the filesystem (Cloud-safe):

```
User clicks [Try Demo]
    ↓
st.session_state["mode"] = "demo"
    ↓
[Generate Demo Deck] button appears
    ↓
User clicks [Generate Demo Deck]
    ↓
Path("demo/apple_financials.xlsx").read_bytes()  →  BytesIO(raw_bytes)
    ↓
run_pipeline(BytesIO(raw_bytes))  →  pptx_bytes
    ↓
st.session_state["pptx_bytes"] = pptx_bytes
    ↓
st.download_button(data=pptx_bytes, file_name="apple_demo.pptx")
```

**Why BytesIO and not Path:** `run_pipeline()` already accepts `Union[str, Path, BinaryIO]`. Passing a `BytesIO` is the pattern already used for uploaded files — confirmed by inspecting `pipeline.py` and `parser.py` signatures. No code change needed in the pipeline.

**Path assumption:** `demo/apple_financials.xlsx` is relative to the working directory when `streamlit run app.py` is called from the project root. On Streamlit Cloud this holds because the repo root is the working directory. Use `Path(__file__).parent / "demo" / "apple_financials.xlsx"` in `app.py` for robustness.

---

## Data Flow: Template Download

The Excel template download does not call the pipeline at all:

```
User clicks [Download Excel Template]
    ↓
Path(__file__).parent / "demo" / "apple_financials.xlsx"
    ↓
st.download_button(
    label="Download Excel Template",
    data=template_path.read_bytes(),
    file_name="autopitch_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)
```

**Static file serving is not needed.** Streamlit's `st.download_button` handles binary files with the correct MIME type. No `./static/` directory or `enableStaticServing` config is required. (Verified: Streamlit static file serving sends `.xlsx` as `Content-Type: text/plain`, making it unusable for direct download links.)

---

## Data Flow: API Key on Streamlit Cloud

The existing `narrative.py` reads `os.environ.get("ANTHROPIC_API_KEY")`. On Streamlit Cloud, root-level secrets in `.streamlit/secrets.toml` automatically become environment variables — confirmed via official docs.

```
Streamlit Cloud Settings → Secrets UI:
  ANTHROPIC_API_KEY = "sk-ant-..."

    ↓  (Streamlit injects as env var at startup)

os.environ["ANTHROPIC_API_KEY"]  ←  narrative.py reads this

No code change needed in autopitch/narrative.py
```

**Local dev change:** Replace (or supplement) `.env` with `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml  (gitignored)
ANTHROPIC_API_KEY = "sk-ant-..."
```

Then remove `load_dotenv()` from `app.py` — `st.secrets` automatically loads secrets before the script runs. Or keep `load_dotenv()` as a fallback for developers who prefer `.env`; both work simultaneously since `os.environ` is populated either way.

**Recommendation:** Keep `load_dotenv()` in `app.py`. Local developers can use either `.env` or `.streamlit/secrets.toml`. Streamlit Cloud ignores `.env` (not present) and uses its own secrets injection. Zero conflict.

---

## Streamlit Session State Pattern

Without session state management, Streamlit reruns the full script on every widget interaction. The existing `app.py` has no session state, which is fine for its 38 lines. The expanded v1.1 UI needs state to:

1. Track which mode the user is in (demo vs. upload)
2. Cache generated PPTX bytes so the download button persists after generation without re-running the pipeline

```python
# Pattern: gate-and-cache
if "pptx_bytes" not in st.session_state:
    st.session_state["pptx_bytes"] = None
if "mode" not in st.session_state:
    st.session_state["mode"] = None  # "demo" | "upload" | None

# Demo button
if st.button("Try the Demo"):
    st.session_state["mode"] = "demo"
    st.session_state["pptx_bytes"] = None  # clear previous result

# Generation gate
if st.session_state["mode"] == "demo" and st.button("Generate Demo Deck"):
    with st.spinner("Generating..."):
        raw = Path(__file__).parent / "demo" / "apple_financials.xlsx"
        pptx_bytes = run_pipeline(io.BytesIO(raw.read_bytes()))
        st.session_state["pptx_bytes"] = pptx_bytes

# Download button persists after generation
if st.session_state["pptx_bytes"]:
    st.download_button("Download PPTX", data=st.session_state["pptx_bytes"], ...)
```

---

## Streamlit Cloud Deployment Integration Points

### Repository Requirements

- Repository can be **public or private** (Community Cloud supports both)
- Public repo: app is public by default
- Private repo: app is private by default; viewers must be granted access explicitly
- The `ANTHROPIC_API_KEY` must **never** be committed — it lives only in Cloud secrets settings

### Dependency File

Streamlit Cloud reads `requirements.txt` from the project root. The existing `requirements.txt` already lists all needed packages. No changes needed except verifying `streamlit` is pinned there (it is: `streamlit>=1.55.0`).

Streamlit itself is pre-installed on Community Cloud — the `streamlit>=1.55.0` pin in `requirements.txt` controls which version is used.

### Python Version

Community Cloud defaults to Python 3.12. The existing codebase targets 3.11+. No conflict — either works. Select version via "Advanced settings" dropdown during deployment.

### Entry Point

Streamlit Cloud needs to know which file is the app entry point. For this project: `app.py` at the repo root. This is the default; no special configuration file needed.

### Secrets Configuration

```
Cloud deployment process:
1. share.streamlit.io → Create app
2. Repo: [your-username]/Autopitch
3. Branch: main
4. Main file: app.py
5. Advanced settings → Secrets:
   ANTHROPIC_API_KEY = "sk-ant-..."
6. Deploy
```

After deployment, secrets can be updated in app settings without redeployment.

---

## Suggested Build Order for v1.1

Dependencies are shallow — most tasks are parallel. The only hard dependency is that Cloud deployment must come last (after UI is complete).

```
Task 1: Secrets config
  → Add .streamlit/secrets.toml (local)
  → Add to .gitignore
  → Remove or keep load_dotenv() (keep for backward compat)
  No dependencies. Can be done first.

Task 2: App.py restructure — hero + demo section
  → Add hero section with landing copy
  → Add [Try Demo] button + session state wiring
  → Add demo generation flow (BytesIO from bundled file)
  → Add PPTX download button
  Depends on: Task 1 (need API key working in new config)

Task 3: App.py — template download section
  → Add st.expander or st.tabs for upload section
  → Wire existing file_uploader flow into new layout
  → Add [Download Excel Template] button (reads demo/apple_financials.xlsx)
  → Add in-app format instructions (from TEMPLATE_FORMAT.md content)
  Depends on: Task 2 (layout already established)

Task 4: App.py — skills showcase section
  → Add st.columns grid of technology badges
  → Static markdown content; no pipeline interaction
  Depends on: Task 3 (bottom of page, natural flow)

Task 5: Polish pass
  → st.set_page_config title/icon/layout tweaks
  → Column widths, spacing, copy review
  → Test full flow locally with demo data
  Depends on: Tasks 2-4 complete

Task 6: Streamlit Cloud deployment
  → Push to GitHub (public or private repo)
  → share.streamlit.io → deploy → add secrets
  → Verify demo flow end-to-end on Cloud
  Depends on: Task 5 complete and all tests passing
```

---

## Architectural Patterns

### Pattern 1: Mode-Gated Session State

**What:** Store current UI mode ("demo" / "upload" / None) in `st.session_state`. Each mode renders a different set of widgets. Generation results (PPTX bytes) cached in state to survive reruns.

**When to use:** Any Streamlit app where a button click should change what is displayed, or where a heavy computation should not re-run on every widget interaction.

**Trade-offs:** Small state footprint (two keys). Keeps app.py logic sequential and readable. The only risk is stale state if the user switches modes — clear `pptx_bytes` when mode changes.

### Pattern 2: BytesIO Pass-Through for Demo Data

**What:** Load bundled Excel file with `Path(...).read_bytes()`, wrap in `io.BytesIO()`, pass directly to `run_pipeline()`. Never write to disk.

**When to use:** Any Streamlit Cloud scenario where the pipeline accepts BinaryIO — disk write access on Cloud is restricted.

**Trade-offs:** Zero-cost: the existing parser already accepts BinaryIO. This is exactly how uploaded files work today. The only addition is reading the local file into bytes first.

### Pattern 3: Root-Level Secrets as Environment Variables

**What:** Store `ANTHROPIC_API_KEY` as a root-level key in `.streamlit/secrets.toml` (local) or Streamlit Cloud's secrets UI. Streamlit automatically injects root-level secrets as environment variables at startup — `os.environ["ANTHROPIC_API_KEY"]` is populated without any code change.

**When to use:** Any Streamlit app that calls external APIs via the standard `os.environ` pattern.

**Trade-offs:** No code changes needed in `narrative.py`. Works alongside `python-dotenv` without conflict (both populate `os.environ`). Secrets are never in source code.

---

## Anti-Patterns

### Anti-Pattern 1: Running the Pipeline in Every Section Independently

**What people do:** Call `run_pipeline()` in both the demo section and the upload section handler, without caching in session state. Each widget interaction that causes a rerun fires the pipeline again.

**Why it's wrong:** Each pipeline run makes a Claude API call (~$0.01 and ~5-10 seconds). Without caching, clicking any widget after generation (e.g., the download button) re-runs the pipeline, doubling cost and latency.

**Do this instead:** Cache `pptx_bytes` in `st.session_state` after the first generation. Gate re-generation behind explicit button clicks. Check `if "pptx_bytes" in st.session_state` before showing the download button.

### Anti-Pattern 2: Hardcoding the Demo File Path as a String

**What people do:** `run_pipeline("demo/apple_financials.xlsx")` — passes a relative path string.

**Why it's wrong:** Relative paths are resolved from the current working directory, which differs between `streamlit run app.py` (project root) and Streamlit Cloud (also project root, but fragile). If `app.py` is ever moved, the path breaks.

**Do this instead:** `Path(__file__).parent / "demo" / "apple_financials.xlsx"` — always resolves relative to the script file, regardless of working directory.

### Anti-Pattern 3: Using Static File Serving for Template Download

**What people do:** Put `apple_financials.xlsx` in `./static/`, set `enableStaticServing = true`, link directly to the file URL.

**Why it's wrong:** Streamlit serves non-image/non-font files as `Content-Type: text/plain`. Browsers render `.xlsx` as garbled text instead of triggering a download. The feature is not designed for binary file distribution.

**Do this instead:** `st.download_button(data=Path(...).read_bytes(), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")` — correct MIME type, proper download trigger.

### Anti-Pattern 4: Putting API Key Logic in app.py

**What people do:** Add `if "ANTHROPIC_API_KEY" not in st.secrets: st.error(...)` guards in the UI, or conditionally skip narrative based on UI-layer checks.

**Why it's wrong:** The pipeline already handles missing API key gracefully — `generate_narrative()` returns a placeholder `NarrativeOutput()` when the key is absent. Duplicating this check in the UI layer creates two sources of truth.

**Do this instead:** Let the pipeline's existing fallback behavior handle it. The UI should only show/hide a non-blocking informational warning if no key is present (e.g., `st.info("No API key — deck will use placeholder narrative.")`).

---

## Integration Points Summary

| Integration | Files Involved | What Changes |
|-------------|---------------|--------------|
| One-click demo | `app.py` | New: demo button, BytesIO load from `demo/apple_financials.xlsx`, session_state wiring |
| Template download | `app.py` | New: `st.download_button` pointing at demo xlsx (or separate template file) |
| Skills showcase | `app.py` | New: static `st.columns` section, no pipeline interaction |
| API key on Cloud | `.streamlit/secrets.toml` (new file) | New local secrets file; existing `os.environ` access in `narrative.py` unchanged |
| Cloud deployment | None (config only) | `requirements.txt` already present; `app.py` at root already valid entry point |
| Pipeline | `autopitch/` package | **No changes** — all v1.0 modules are unchanged |

---

## Scaling Considerations

This is a portfolio demo tool. Streamlit Community Cloud free tier is the only deployment target.

| Concern | Reality | Approach |
|---------|---------|----------|
| Concurrent demo users | Community Cloud is resource-constrained; pipeline is stateless so concurrent sessions are safe | Each session runs independently; no shared state across users |
| Claude API cost per demo run | ~$0.01/run | Not a concern for a portfolio demo with low traffic; session_state caching prevents duplicate calls within a session |
| Demo file size | `apple_financials.xlsx` is small (<100KB) | Read into memory per button click; negligible overhead |
| Cold start latency on Cloud | Apps "sleep" after inactivity; first load may be slow | No mitigation needed for a portfolio demo; first load lag is expected behavior |

---

## Sources

- Streamlit secrets management (official): https://docs.streamlit.io/develop/concepts/connections/secrets-management — HIGH confidence
- Streamlit Community Cloud deployment (official): https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy — HIGH confidence
- Streamlit app dependencies (official): https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies — HIGH confidence
- Streamlit static file serving (official): https://docs.streamlit.io/develop/concepts/configuration/serving-static-files — HIGH confidence (XLSX not supported for static serving — confirmed)
- Streamlit layout components (official): https://docs.streamlit.io/develop/api-reference/layout — HIGH confidence
- Existing codebase directly inspected: `app.py`, `generate.py`, `autopitch/pipeline.py`, `autopitch/models.py`, `autopitch/narrative.py`, `requirements.txt` — HIGH confidence

---

*Architecture research for: Autopitch v1.1 Portfolio Demo Polish*
*Researched: 2026-03-10*
*Scope: Integration of portfolio UI features with existing v1.0 pipeline — pipeline itself unchanged*

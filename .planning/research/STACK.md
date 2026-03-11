# Technology Stack

**Project:** Autopitch v1.1 — Portfolio Demo Polish
**Domain:** Streamlit portfolio UI — demo experience, skills showcase, Cloud deployment
**Researched:** 2026-03-10
**Confidence:** HIGH (verified against official Streamlit docs and Community Cloud documentation)

> **Scope:** This document covers ONLY stack additions and changes needed for v1.1.
> The v1.0 stack (python-pptx, matplotlib, openpyxl, Pydantic v2, anthropic SDK, Streamlit basics)
> is already shipped and validated. Do not re-evaluate or re-install those packages.

---

## What v1.1 Needs From the Stack

| Capability | Source | Verdict |
|------------|--------|---------|
| Demo-first layout (hero, columns, tabs) | Streamlit stdlib | No new package — already in Streamlit |
| One-click Apple demo button | `st.session_state` + `st.button` | No new package |
| Skills/badge showcase | `st.badge` (added in Streamlit v1.55.0) | Requires Streamlit >= 1.55 (already in requirements.txt) |
| Downloadable Excel template | `openpyxl` (already installed) + `io.BytesIO` | No new package |
| UI theming / polished look | `.streamlit/config.toml` | Config file only, no new package |
| Secrets on Community Cloud | `.streamlit/secrets.toml` + `st.secrets` | Config file only, no new package |
| Streamlit Cloud deployment | `requirements.txt` (already exists) + GitHub | No new package; one new config file |

**Net result: zero new Python packages required for v1.1.** All capabilities are either in the
existing Streamlit version (>=1.55.0 already pinned) or achieved through configuration files.

---

## Recommended Stack Additions

### New Files (Config, Not Code)

| File | Purpose | Why |
|------|---------|-----|
| `.streamlit/config.toml` | App theming — colors, font, layout | Community-standard approach for Streamlit brand polish. Sets `primaryColor`, `backgroundColor`, `layout = "wide"`. No CSS hacks needed for basic visual hierarchy. |
| `.streamlit/secrets.toml` | Local secrets mirror (gitignored) | Enables `st.secrets["ANTHROPIC_API_KEY"]` locally. Streamlit Community Cloud reads secrets from the dashboard, not from `.env`, so `python-dotenv` approach must be supplemented. |

### Streamlit Features to Use (Already Available in >= 1.35)

These are built-in Streamlit capabilities — no install needed, just need to be used in `app.py`.

| Feature | API | Purpose | Notes |
|---------|-----|---------|-------|
| Tabbed layout | `st.tabs(["Demo", "Upload", "How It Works"])` | Organize content into clear sections | Available since Streamlit 1.29 |
| Column layout | `st.columns([1, 2])` | Side-by-side hero layout, badge grid | Core Streamlit, always available |
| Session state | `st.session_state` | Track demo mode vs. upload mode; persist generated deck bytes | Needed so "Generate Demo" button result survives reruns |
| Caching for demo data | `@st.cache_data` | Load `demo/apple_financials.xlsx` once as bytes, not per user rerun | Avoids re-reading disk on every interaction |
| Badge | `st.badge(label, color, icon)` | Tech stack skill tags — "Python", "Claude API", "Streamlit" | Added in Streamlit v1.55.0; confirmed in official docs |
| Expander | `st.expander("Excel format guide")` | Collapsible instructions for custom upload | Keeps UI clean; lazy-renders content |
| Download button | `st.download_button()` | Already used in v1.0 for PPTX; same pattern for Excel template | No change needed |

---

## Secrets Management for Cloud Deployment

### The Problem

`python-dotenv` reads `.env` files, which are gitignored and not present on Streamlit Community Cloud.
The current `app.py` calls `load_dotenv()` before pipeline execution. This works locally but the
`ANTHROPIC_API_KEY` is missing on Cloud without additional handling.

### The Solution

Streamlit's `st.secrets` system automatically exposes top-level TOML keys as environment variables.
This means `os.environ["ANTHROPIC_API_KEY"]` will work on Cloud if the key is set in the Community
Cloud dashboard — no code change needed to the `anthropic` SDK call itself.

**Required change in `app.py`:** Add a `st.secrets` fallback before `load_dotenv()`:

```python
import os
import streamlit as st
from dotenv import load_dotenv

# Load from .env locally; on Streamlit Cloud, st.secrets populates os.environ automatically.
# Explicitly bridge st.secrets → os.environ as a safety net for any execution order issues.
if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]
load_dotenv()  # still useful locally; no-op on Cloud if .env absent
```

**Local `.streamlit/secrets.toml` format** (gitignored, mirrors `.env`):

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

**Community Cloud setup:** Paste the secrets.toml contents into App Settings → Secrets in the
Streamlit Community Cloud dashboard. Updated without redeployment.

---

## Streamlit Community Cloud Deployment Requirements

### What Community Cloud Needs

| Requirement | Status | Action |
|-------------|--------|--------|
| Public GitHub repo | Existing repo | Ensure repo is public (or linked private) |
| `requirements.txt` in repo root | Already exists | Verify all packages listed; Streamlit itself is optional to list |
| Python version selection | Defaults to latest (3.13) | Explicitly select 3.11 in "Advanced settings" during deploy dialog to match local dev |
| `ANTHROPIC_API_KEY` secret | In `.env` locally | Paste into Community Cloud dashboard secrets after deploy |
| `packages.txt` | Not needed | No system-level apt dependencies (no C extensions, no binary tools) |
| Entry point | `app.py` at repo root | Already correct |

### Python Version Pin

Community Cloud now defaults to Python 3.13 (confirmed via community discussion March 2026).
The project targets Python 3.11 (`pyproject.toml` specifies `requires-python = ">=3.11"`).
Select Python 3.11 explicitly in the deploy dialog's Advanced settings — you cannot change it
after deployment without deleting and redeploying the app.

**HIGH confidence** — Official Streamlit docs + community forum confirmation (multiple threads).

### `requirements.txt` for Cloud

The current `requirements.txt` is adequate. One note: `python-dotenv` must remain listed because
`app.py` imports it. On Cloud the `load_dotenv()` call is a no-op (no `.env` present), but the
import still needs to resolve.

No new packages need to be added.

---

## Downloadable Excel Template

The "Download Excel template" feature uses the existing `openpyxl` package. Pattern:

```python
from io import BytesIO
import openpyxl

@st.cache_data
def build_template_bytes() -> bytes:
    wb = openpyxl.load_workbook("demo/apple_financials.xlsx")
    # Optionally strip data, leaving structure and headers only
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
```

Then `st.download_button(data=build_template_bytes(), file_name="autopitch_template.xlsx")`.

No new package needed — `openpyxl` is already installed and capable of writing to BytesIO.

---

## UI Theming

Streamlit theming is configured via `.streamlit/config.toml`. A minimal dark/professional theme
appropriate for a financial tool:

```toml
[theme]
base = "light"
primaryColor = "#1B3A6B"       # Navy — Big 4 consulting anchor color
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F4F6FA"
textColor = "#1A1A2E"
font = "sans serif"
```

This file is committed to the repo (no secrets) and applies both locally and on Cloud.

**No external CSS injection needed** for the v1.1 scope. `st.markdown(unsafe_allow_html=True)` with
custom CSS is an option but adds fragile maintenance surface — avoid unless theming config.toml
proves insufficient for specific layout needs.

---

## Alternatives Considered

| Recommended | Alternative | Why Not |
|-------------|-------------|---------|
| `st.badge` for skill tags | Custom HTML badges via `st.markdown(unsafe_allow_html=True)` | st.badge is the official API (added v1.55.0); HTML injection is fragile across Streamlit upgrades |
| `.streamlit/config.toml` for theming | CSS injection via `st.markdown` | config.toml is the stable, supported path; CSS injection bypasses the theming system and breaks on Streamlit updates |
| `st.tabs` for layout sections | Separate Streamlit pages (multipage app) | Multipage adds navigation complexity and breaks the single-URL demo flow; tabs keep everything on one screen |
| `@st.cache_data` for demo bytes | Re-reading demo file on each rerun | cache_data runs once per session and is the documented pattern for file loading in Streamlit |
| `st.secrets` + `os.environ` bridge | Rewrite pipeline to read `st.secrets` directly | Pipeline has no Streamlit dependency and should stay that way; os.environ bridge keeps pipeline clean |
| Streamlit Community Cloud | Render / Heroku / Railway | Community Cloud is free, zero-config, Streamlit-native; handles Python env + secrets natively; best fit for a portfolio demo |

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `streamlit-extras` | Third-party component library; adds dependency for minor UI niceties | Native Streamlit has everything needed for v1.1 |
| `streamlit-option-menu` | Third-party nav component; overkill for a 2-3 section layout | `st.tabs` is built-in and sufficient |
| `plotly` | Adds ~30MB to deploy footprint; interactive charts don't embed in PPTX anyway | `matplotlib` (already used) handles all charting |
| `xlsxwriter` | Separate Excel-write library; openpyxl already handles write-to-BytesIO | `openpyxl` (already installed) |
| Additional AI/ML libraries | Out of scope for UI polish milestone | N/A |

---

## Version Compatibility

| Package | Current Pin | Notes |
|---------|-------------|-------|
| `streamlit` | `>=1.55.0` | v1.55.0 introduced `st.badge`; already pinned in requirements.txt |
| `openpyxl` | `>=3.1.0` | Write-to-BytesIO supported since 3.x; no change needed |
| `python-dotenv` | `>=1.0.0` | Retain; load_dotenv() is a no-op on Cloud, harmless |

No version bumps required. No new packages required.

---

## Sources

- [Streamlit Community Cloud — App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — Python version, requirements.txt behavior, packages.txt — HIGH confidence
- [Streamlit Community Cloud — Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management) — secrets.toml format, dashboard upload — HIGH confidence
- [Streamlit secrets management concepts](https://docs.streamlit.io/develop/concepts/connections/secrets-management) — st.secrets as env vars, dotenv coexistence — HIGH confidence
- [st.badge API reference](https://docs.streamlit.io/develop/api-reference/text/st.badge) — version introduced (v1.55.0), parameters — HIGH confidence
- [Streamlit theming: colors and borders](https://docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders) — config.toml options — HIGH confidence
- [Streamlit community forum: Python 3.13 default on Cloud](https://discuss.streamlit.io/t/streamlit-cloud-using-python-3-13-despite-runtime-txt-specifying-3-11/113759) — Python version default behavior — MEDIUM confidence (community, not official docs)

---
*Stack research for: Autopitch v1.1 Portfolio Demo Polish*
*Researched: 2026-03-10*

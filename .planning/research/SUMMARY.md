# Project Research Summary

**Project:** Autopitch v1.1 — Portfolio Demo Polish
**Domain:** Streamlit portfolio UI — demo experience, skills showcase, Cloud deployment
**Researched:** 2026-03-10
**Confidence:** HIGH

## Executive Summary

Autopitch v1.1 is a pure UI-layer enhancement to a fully working v1.0 pipeline. The goal is to transform a bare Streamlit file-uploader into a portfolio-ready live demo accessible to recruiters and interviewers who arrive without their own data. All research converges on the same architectural conclusion: the existing `autopitch/` package requires zero changes — every v1.1 feature is implemented in `app.py` and two new config files (`.streamlit/config.toml`, `.streamlit/secrets.toml`). No new Python packages are needed; all required UI capabilities already exist in the pinned Streamlit version (>=1.55.0).

The recommended approach is a four-section UI restructure: hero landing with a one-click Apple demo, followed by an upload-your-own section with instructions and template download, then a skills/tech showcase at the bottom. The dependency chain is shallow — most tasks within the milestone are independent and can be parallelized — with one hard ordering constraint: Streamlit Community Cloud deployment must come last.

The primary risks are deployment-specific, not architectural. Three blockers must be resolved before the app goes live: `python-pptx` and `matplotlib` are confirmed missing from `requirements.txt` (guaranteed `ModuleNotFoundError` on Cloud at runtime), dev dependencies (`pytest`, `pytest-cov`) must be moved to a separate `requirements-dev.txt` to avoid build conflicts, and the GitHub repository has a push authentication issue (403 on tag push) that must be resolved before any Cloud deployment can proceed. Additionally, the `st.session_state` pattern must be implemented correctly to prevent generated deck bytes from disappearing when the download button is clicked — a well-documented Streamlit rerun gotcha that affects every app that produces downloadable artifacts.

## Key Findings

### Recommended Stack

The v1.1 stack is the v1.0 stack with two new config files and zero new Python packages. Streamlit >= 1.55.0 already provides every UI primitive needed: `st.tabs`, `st.columns`, `st.badge` (added v1.55.0), `st.expander`, `st.download_button`, and `st.session_state`. The one non-trivial stack concern is secrets management: on Streamlit Community Cloud, `python-dotenv`'s `load_dotenv()` is a no-op because `.env` is gitignored and absent on Cloud. The API key must be injected via the Streamlit Cloud dashboard and accessed through `st.secrets`. Root-level TOML secrets are automatically promoted to `os.environ` at app startup, meaning `narrative.py` requires no code changes whatsoever.

**Core technology additions (config files, not packages):**
- `.streamlit/config.toml` — app theming (navy `primaryColor`, wide layout, sans-serif font) — config only, no code
- `.streamlit/secrets.toml` — local API key mirror (gitignored) — enables `st.secrets` for local dev

**Built-in Streamlit features to use (already in >= 1.55.0):**
- `st.session_state` — mode tracking ("demo" / "upload" / None) and PPTX byte caching across reruns
- `@st.cache_data` — memoize the demo pipeline call to prevent duplicate Claude API calls on button re-clicks
- `st.badge` — tech skill tags per the official API added in v1.55.0
- `st.tabs` / `st.columns` / `st.expander` — layout structure for hero, upload section, and skills showcase

**Required `requirements.txt` corrections (confirmed blockers):**
- Add `python-pptx>=1.0.0` — currently absent; Cloud build will fail at runtime without it
- Add `matplotlib>=3.8.0` — currently absent; Cloud build will fail at runtime without it
- Remove `pytest>=8.0.0` and `pytest-cov>=5.0.0` — move to new `requirements-dev.txt`

### Expected Features

All v1.1 features are low-complexity UI composition on top of the existing `run_pipeline()` call. The feature research draws a sharp line between what a portfolio visitor requires (P1) and what is polish after the core is stable (P2).

**Must have (table stakes — P1):**
- Hero / landing section — first impression; raw file uploader as opening element reads as unfinished
- One-click Apple demo button — proof of output is the entire value proposition; visitors will not upload their own data first
- Demo download button — completes the demo loop; a demo with no artifact proves nothing
- Loading spinner during generation — 5-15s API call with no feedback reads as frozen app
- In-app format instructions (accordion) — enables the upload-your-own path credibly
- Downloadable Excel template — `apple_financials.xlsx` doubles as the template; removes format barrier
- Tech stack / skills section with decision rationale — recruiter keyword signal; badge grid, not a raw list
- `requirements.txt` corrected and Streamlit Cloud deployed with API key secret — the milestone is moot without a live URL

**Should have (polish — P2, add once core is stable on Cloud):**
- Generation stats (elapsed time + slide count) — credibility detail grounded in observable evidence
- Visual polish pass (`st.columns`, spacing, section headers, `config.toml` theming)

**Defer to v2+:**
- Multi-company comparison — requires pipeline architecture change
- PDF export — separate deliverable format
- Real-time SEC / Yahoo Finance data ingestion — removes Excel dependency entirely
- In-app slide preview (PPTX to image render) — heavy, fragile on Cloud free tier RAM

**Do not build (anti-features):**
- Always-on ping loop hack — against Streamlit fair-use intent; use GitHub Actions keep-alive cron instead
- Per-slide progress bar — `run_pipeline()` is a single blocking call; faking progress is misleading
- User accounts / saved decks — auth infrastructure out of scope; stateless is correct for a portfolio demo

### Architecture Approach

v1.1 is an `app.py` expansion from 38 lines to approximately 150 lines. The `autopitch/` package is entirely untouched. The architecture follows three explicit patterns established in ARCHITECTURE.md: (1) mode-gated session state (`"demo"` / `"upload"` / `None`) to track UI context and cache generated bytes across reruns, (2) BytesIO pass-through for the demo file so no disk writes occur on Cloud, and (3) root-level secrets-as-env-vars so `narrative.py` reads `os.environ["ANTHROPIC_API_KEY"]` identically in both local and Cloud environments without any code change.

**Major components:**

1. `app.py` (modified — 38 → ~150 lines) — four-section UI: hero with one-click demo, upload path with instructions, template download, skills showcase; session state orchestration
2. `.streamlit/config.toml` (new) — theming: navy `primaryColor = "#1B3A6B"`, wide layout, sans-serif font; committed to repo
3. `.streamlit/secrets.toml` (new, gitignored) — local API key mirror; Cloud uses dashboard settings panel
4. `autopitch/` package — unchanged; `run_pipeline(source: Union[str, Path, BinaryIO]) -> bytes` is the only integration point
5. `requirements.txt` (corrected) — add `python-pptx`, `matplotlib`; remove `pytest`, `pytest-cov`
6. `requirements-dev.txt` (new) — `-r requirements.txt` plus `pytest`, `pytest-cov`
7. GitHub Actions keep-alive workflow (new) — GET request to app URL every 6 hours to prevent Cloud hibernation

**Suggested build order within v1.1:**

```
Task 1: Fix requirements.txt and create requirements-dev.txt — deployment blocker, do first
Task 2: Secrets config (.streamlit/secrets.toml + .gitignore entry) — prerequisite for local testing
Task 3: app.py hero section + one-click demo with session state wiring
Task 4: app.py upload section + template download + format instructions accordion
Task 5: app.py skills showcase section (st.columns badge grid with rationale)
Task 6: Polish pass (config.toml theming, spacing, copy review, local end-to-end test)
Task 7: Cloud deployment (fix GitHub auth, push, deploy, configure secrets, keep-alive workflow)
```

### Critical Pitfalls

**v1.1 deployment blockers (address in Phase 1, before anything else):**

1. **`python-pptx` and `matplotlib` missing from `requirements.txt`** — confirmed absent in the current file. Streamlit Cloud will install only what is listed; both packages are imported at runtime. Add both before the first deployment attempt or the app will `ModuleNotFoundError` immediately on deck generation.

2. **API key committed to public repo** — GitHub secret scanning auto-revokes Anthropic keys within minutes of exposure. Verify `.gitignore` covers both `.env` and `.streamlit/secrets.toml` before making the repo public. Set `ANTHROPIC_API_KEY` only through the Streamlit Cloud dashboard — never in any file that enters version control.

3. **Download button loses generated bytes on rerun** — clicking `st.download_button` triggers a full Streamlit script rerun. `pptx_bytes` defined inside `if st.button("Generate"):` goes out of scope and the download button disappears. Fix: store in `st.session_state["pptx_bytes"]` immediately after generation; render the download button unconditionally from state on every rerun.

4. **Dev dependencies in `requirements.txt` cause Cloud build conflicts** — `pytest` and `pytest-cov` must be split to `requirements-dev.txt` before deployment. Single requirements file for dev+prod is never acceptable for a deployed app.

5. **App hibernation makes the demo invisible to portfolio visitors** — Streamlit Community Cloud sleeps apps after ~12h of no traffic; cold-start wake takes 20-30 seconds. A recruiter who sees the sleep page often clicks away. Add a GitHub Actions keep-alive cron before sharing the live URL. Add a "may take ~30s to wake if inactive" note to the portfolio page.

**v1.1 moderate pitfalls (address during Phase 2):**

6. **One-click demo calls Claude API on every button press** — wrap the demo pipeline call in `@st.cache_data` keyed on the demo file bytes; returns cached PPTX on subsequent clicks within the session. Also catch `anthropic.RateLimitError` with a user-friendly message rather than a raw traceback.

7. **Skills showcase reads as resume padding without rationale** — a badge wall of library names provides zero signal to technical reviewers. Limit to 5-6 technologies, each with one sentence explaining the architectural decision made and why. Link each item to the relevant source file.

8. **File uploader shown before demo** — `st.file_uploader` as the first visible element gates the tool behind a prerequisite most visitors cannot fulfill. Hero section and demo button must be visible above the fold without scrolling.

9. **Excel template download returns corrupt file** — correct MIME type is `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; file must be opened in binary mode (`"rb"`); BytesIO buffer must have `seek(0)` called after write before `.getvalue()`. Test downloaded file opens without Excel repair prompt.

## Implications for Roadmap

Based on the pitfall-to-phase mapping in PITFALLS.md and the dependency graph in ARCHITECTURE.md, a three-phase structure is recommended. The key structural insight: deployment-blocking issues must be resolved before UI work, because every feature built before fixing the requirements file is unverifiable on Cloud.

### Phase 1: Deployment Foundation

**Rationale:** Two confirmed blockers exist right now — missing packages in `requirements.txt` and GitHub push authentication failure. Neither is a UI problem; both will silently prevent the entire milestone from going live. Resolving them first means every subsequent task can be validated incrementally on Cloud rather than discovering a broken deploy at the end. This phase also handles all security setup: secrets gitignore configuration and repo public/private decision.

**Delivers:** Corrected `requirements.txt`, new `requirements-dev.txt`, `.streamlit/secrets.toml` with `.gitignore` entry, GitHub auth restored, first successful Cloud deployment (bare UI acceptable at this stage), API key configured in Cloud dashboard.

**Addresses features:** Table stakes item "live deployed URL"; `requirements.txt` accuracy requirement.

**Avoids pitfalls:** #21 (python-pptx/matplotlib missing), #20 (dev deps in requirements.txt), #17 (API key committed to repo). All three are confirmed present risks that will cause guaranteed failures if not addressed before Phase 2 begins.

### Phase 2: Demo-First UI

**Rationale:** Once the app is deployable, the complete UI restructure can be built and verified on Cloud with each commit. Session state must be established as the first sub-task because `pptx_bytes` persistence is the load-bearing pattern that every button in the demo and upload sections depends on. The four sections of `app.py` are otherwise largely independent and can be built in any order once session state is wired.

**Delivers:** Complete four-section `app.py`: hero with one-click Apple demo and download button, upload section with in-app format instructions accordion and Excel template download, skills showcase with rationale-first badge grid. This is the full portfolio-visible surface area.

**Uses:** `st.session_state`, `st.tabs`, `st.columns`, `st.badge`, `st.expander`, `st.download_button`, `@st.cache_data`, `BytesIO` pass-through, `Path(__file__).parent / "demo" / ...` for Cloud-safe file resolution.

**Avoids pitfalls:** #18 (download button loses bytes — session state), #22 (API called on every click — cache_data), #23 (skills section as padding — rationale-first), #24 (file uploader buried — hero first), #25 (template download corrupt — correct MIME type and binary mode).

### Phase 3: Polish and Keep-Alive

**Rationale:** Visual polish and the keep-alive mechanism are deliberately last. Polishing layout before structure is locked wastes time if sections move. The keep-alive workflow has no value until a live URL exists and the portfolio link is ready to share.

**Delivers:** `.streamlit/config.toml` theming (navy palette, wide layout), generation stats (elapsed time + slide count), column widths and spacing cleanup, GitHub Actions cron keep-alive workflow that pings the app URL every 6 hours.

**Uses:** `.streamlit/config.toml`, `time.time()` wrapper around `run_pipeline()` call, GitHub Actions workflow YAML (cron schedule, HTTP GET to app URL).

**Avoids pitfall:** #19 (app sleeping when portfolio link is shared). This phase must complete before the live URL is publicized.

### Phase Ordering Rationale

- **Deployment before UI:** The two missing packages in `requirements.txt` are a confirmed hard failure. Every feature built before fixing this is unverifiable on Cloud. Resolve blockers first, then build on a verified foundation.
- **Session state before demo flow:** `st.session_state["pptx_bytes"]` persistence is the pattern every button in the demo and upload sections depends on. Establishing it as the first sub-task in Phase 2 prevents retrofitting it into all subsequent sub-tasks.
- **Keep-alive and polish last:** Both require a live URL (keep-alive) or locked structure (polish). Building them earlier wastes effort.
- **Uniform shallow dependency depth:** Unlike v1.0 (which had a strict linear pipeline dependency chain), v1.1's tasks are mostly parallel within each phase. The phase boundaries reflect deployment readiness checkpoints, not data dependency constraints.

### Research Flags

Phases with standard, well-documented patterns — no `/gsd:research-phase` needed during planning:

- **Phase 1 (Deployment Foundation):** All steps (requirements.txt correction, .gitignore, .streamlit/secrets.toml, Cloud deployment process) are covered verbatim with code examples in STACK.md and PITFALLS.md. Official Streamlit docs verified.
- **Phase 2 (Demo-First UI):** Session state patterns, BytesIO flow, `@st.cache_data` usage, all widget APIs, and complete code sketches for every data flow are provided in ARCHITECTURE.md. No unknowns remain.
- **Phase 3 (Polish and Keep-Alive):** Streamlit config.toml theming and GitHub Actions cron are standard, extensively documented patterns. No research gap.

No phases require deeper research during planning. All research was resolved at the project-level stage with official documentation.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Zero new packages needed. All capabilities in Streamlit >= 1.55.0 which is already pinned. Official docs verified for every listed feature. |
| Features | HIGH (Streamlit behavior) / MEDIUM (UX conventions) | Streamlit Cloud behavior (sleep, secrets, requirements.txt) verified against official docs. Hero-first, demo-first UX conventions are community-supported but not from a single authoritative source — acceptable risk given the low-stakes nature of the decision. |
| Architecture | HIGH | Existing codebase directly inspected. `run_pipeline()` and `parse_workbook()` signatures confirmed. Session state patterns and BytesIO pass-through are standard, well-documented Streamlit practices with code examples in the official docs. |
| Pitfalls | HIGH (v1.1) | v1.1 pitfalls verified against official Streamlit and Anthropic docs. The two missing packages (python-pptx, matplotlib) are confirmed by direct inspection of the current `requirements.txt`. |

**Overall confidence:** HIGH

### Gaps to Address

- **GitHub push authentication (403 error):** The MEMORY.md notes that `git push` for the v1.0 tag failed with a 403 permission denied error. This is the only external blocker not fully resolved by research. Resolution: re-authenticate via `gh auth login` or regenerate a personal access token before Phase 1 deployment work begins. This must be resolved before any Cloud deployment task can be attempted.

- **Python version on Streamlit Cloud:** The STACK.md research noted that Community Cloud now defaults to Python 3.13 (one community forum source, MEDIUM confidence). The project targets Python 3.11+. Python 3.11 must be selected explicitly in the deploy dialog's Advanced Settings during the first deployment — it cannot be changed after deployment without deleting and redeploying the app. Confirm this during Phase 1.

- **matplotlib figure memory leak on Cloud:** PITFALLS.md identifies that `plt.close('all')` must be called after each chart is saved to BytesIO to prevent memory growth across repeated deck generations in one session. The existing `charts.py` should be audited for this one-liner. Minor risk given low traffic of a portfolio demo, but worth a one-line verification before Cloud deployment.

## Sources

### Primary (HIGH confidence)
- [Streamlit Community Cloud — App dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies) — requirements.txt behavior, Python version selection
- [Streamlit Community Cloud — Secrets management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management) — secrets.toml format, dashboard upload, env var injection
- [Streamlit secrets concepts](https://docs.streamlit.io/develop/concepts/connections/secrets-management) — st.secrets as env vars, dotenv coexistence
- [st.badge API reference](https://docs.streamlit.io/develop/api-reference/text/st.badge) — version introduced (v1.55.0), parameters
- [Streamlit theming: colors and borders](https://docs.streamlit.io/develop/concepts/configuration/theming-customize-colors-and-borders) — config.toml options
- [Streamlit Community Cloud — Status and Limitations](https://docs.streamlit.io/deploy/streamlit-community-cloud/status) — sleep behavior, free tier constraints
- [st.download_button docs](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button) — binary file handling, MIME types
- [Streamlit — Button behavior and examples](https://docs.streamlit.io/develop/concepts/design/buttons) — rerun behavior, state patterns
- [Streamlit — Serving static files](https://docs.streamlit.io/develop/concepts/configuration/serving-static-files) — confirmed XLSX not suitable for static serving (Content-Type: text/plain)
- [Streamlit blog — 8 tips for securely using API keys](https://blog.streamlit.io/8-tips-for-securely-using-api-keys/) — key security best practices
- [Anthropic — API Key Best Practices](https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure) — key exposure risk
- [Anthropic — Rate limits](https://docs.anthropic.com/en/api/rate-limits) — 429 behavior
- Existing codebase directly inspected: `app.py`, `autopitch/pipeline.py`, `autopitch/narrative.py`, `requirements.txt`

### Secondary (MEDIUM confidence)
- [Streamlit community — Python 3.13 default on Cloud](https://discuss.streamlit.io/t/streamlit-cloud-using-python-3-13-despite-runtime-txt-specifying-3-11/113759) — Python version default (community post, not official docs)
- [Streamlit community — Download button loses result output](https://discuss.streamlit.io/t/download-button-reloads-app-and-results-output-is-gone-and-need-to-re-run/51467) — session state fix corroboration
- [Streamlit community — App sleeping behavior](https://discuss.streamlit.io/t/how-to-prevent-the-app-enter-the-sleep-mode/87959) — sleep duration and keep-alive approaches
- [Portfolio UX patterns (WeAreDevelopers March 2025)](https://www.wearedevelopers.com/en/magazine/561/web-developer-portfolio-inspiration-and-examples-march-2025-561) — hero-first, demo-first conventions
- [Streamlit blog — Common app problems: Resource limits](https://blog.streamlit.io/common-app-problems-resource-limits/) — matplotlib memory and Cloud RAM constraints

### Tertiary (LOW confidence)
- [Building a Portfolio with Streamlit (Medium)](https://medium.com/data-science-in-your-pocket/building-portfolio-using-streamlit-ac215b8e74da) — structural patterns, single source

---
*Research completed: 2026-03-10*
*Ready for roadmap: yes*

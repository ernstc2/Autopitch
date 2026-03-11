---
phase: 06-demo-first-ui
plan: 01
subsystem: ui
tags: [streamlit, session-state, cache-data, openpyxl, pptx, demo]

# Dependency graph
requires:
  - phase: 05-deployment-foundation
    provides: Streamlit Cloud deployment; confirmed on_click="ignore" works with streamlit>=1.55.0
  - phase: 04-streamlit-ui
    provides: run_pipeline() and ValidationError from autopitch.pipeline / autopitch.models
provides:
  - Hero landing section explaining Autopitch before any interactive widget
  - _run_demo_pipeline() cached with @st.cache_data for Apple demo data
  - st.session_state persistence for demo_pptx, demo_elapsed, demo_slides
  - on_click="ignore" on all download buttons preventing disappear-on-rerun
  - _build_template_xlsx() returning valid XLSX bytes (PK magic)
  - Upload section with session state persistence for upload_pptx
  - Tech stack section scaffold (6 technologies)
affects:
  - 06-02-PLAN (upload format guide and tech stack expansion build on this app.py structure)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Session state guard pattern: for key in (...): if key not in st.session_state: st.session_state[key] = None"
    - "@st.cache_data(show_spinner=False) on fixed-input demo pipeline; NOT on upload path"
    - "Download button with on_click='ignore' rendered outside if-button block based on session_state"
    - "Structural UI tests: read app.py source as text, verify patterns with regex + line ordering"
    - "App module test isolation: mock st.button.return_value=False, st.file_uploader.return_value=None"

key-files:
  created:
    - tests/test_ui.py
  modified:
    - app.py

key-decisions:
  - "on_click='ignore' on ALL download buttons — prevents rerun that would hide download button"
  - "Download buttons rendered outside if-button blocks — persists across all reruns"
  - "Slide count hardcoded as 11 — deck always produces exactly 11 slides; avoid wasteful re-parse"
  - "Test isolation via mock: st.button=False, st.file_uploader=None, st.columns returns 2-item list"

patterns-established:
  - "Pattern: Session state initialization guard at top of app.py before any widget rendering"
  - "Pattern: @st.cache_data wraps demo pipeline (no args = fixed cache key); upload path never cached"
  - "Pattern: Structural Streamlit tests inspect app.py source text rather than using AppTest runtime"

requirements-completed: [DEMO-01, DEMO-02, DEMO-03, DEMO-04]

# Metrics
duration: 7min
completed: 2026-03-11
---

# Phase 06 Plan 01: Demo-First UI Summary

**Hero + one-click demo rewrite of app.py with session state persistence, @st.cache_data on Apple pipeline, and on_click="ignore" download buttons that survive reruns**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-11T01:21:13Z
- **Completed:** 2026-03-11T01:28:14Z
- **Tasks:** 2 (TDD: RED commit + GREEN commit)
- **Files modified:** 2 (app.py, tests/test_ui.py)

## Accomplishments

- Rewrote app.py from 38-line minimal uploader into structured portfolio page with hero, demo, upload, and tech stack sections
- Implemented session state persistence pattern so download button survives all reruns (DEMO-03)
- Created 12-test structural test suite covering DEMO-01 through DEMO-04 plus UPLD-03 (_build_template_xlsx)
- Full test suite passes: 74 tests, 0 failures, no regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Create UI test scaffold and write failing tests (RED)** - `f1369de` (test)
2. **Task 2: Rewrite app.py with hero section and demo generation flow (GREEN)** - `ee72f5f` (feat)

**Plan metadata:** (docs commit — created after SUMMARY.md)

_Note: TDD tasks — RED commit (failing tests), GREEN commit (implementation makes all pass)_

## Files Created/Modified

- `app.py` — Complete rewrite: hero section, cached demo pipeline, session state, upload with persistence, tech stack section
- `tests/test_ui.py` — 12 structural tests covering DEMO-01 through DEMO-04 and UPLD-03

## Decisions Made

- **on_click="ignore" on all download buttons:** Prevents the rerun that would cause the download button to disappear. Available since Streamlit 1.43.0; project requires >= 1.55.0.
- **Download buttons outside if-button blocks:** Buttons rendered conditionally on `st.session_state["demo_pptx"] is not None` — survives any subsequent widget interaction.
- **Slide count hardcoded as 11:** Deck always produces exactly 11 slides. Hardcoding avoids expensive PPTX re-parse via `Presentation(BytesIO(bytes))`.
- **Test isolation approach:** Mocking streamlit with `st.button.return_value=False` and `st.file_uploader.return_value=None` prevents pipeline execution during module import; `st.columns.return_value=[mock, mock]` enables tuple unpacking.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed `st.columns` unpacking failure in test isolation**
- **Found during:** Task 2 (GREEN phase — running UI tests after app.py rewrite)
- **Issue:** Test for `_build_template_xlsx` imported app module with mocked Streamlit but `st.columns()` returned a MagicMock that couldn't be unpacked into two variables. Also `st.button` defaulted to truthy causing pipeline execution with MagicMock file path.
- **Fix:** Added `st_mock.columns.return_value = [col_mock, col_mock]`, `st_mock.button.return_value = False`, `st_mock.file_uploader.return_value = None` to test mock configuration.
- **Files modified:** tests/test_ui.py
- **Verification:** All 12 UI tests pass, 74 total tests pass
- **Committed in:** ee72f5f (Task 2 feat commit)

**2. [Rule 1 - Bug] Removed `build_deck` string from app.py comment**
- **Found during:** Task 2 (full suite regression check)
- **Issue:** `test_no_pipeline_calls_in_app` does a string search for forbidden names including `build_deck`. A comment `# always; from build_deck() docstring` triggered the assertion failure.
- **Fix:** Changed comment to `# deck always produces exactly 11 slides`.
- **Files modified:** app.py
- **Verification:** `test_no_pipeline_calls_in_app` passes; full suite green.
- **Committed in:** ee72f5f (Task 2 feat commit — part of same fix pass)

---

**Total deviations:** 2 auto-fixed (both Rule 1 bugs)
**Impact on plan:** Both fixes were necessary for test correctness. No scope creep.

## Issues Encountered

None beyond the two auto-fixed bugs documented above.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- app.py is ready for Plan 06-02 to add: format guide expander, template download in upload section, and expanded tech stack badges
- Session state keys `upload_pptx` already initialized and used — Plan 06-02 upload flow can build directly
- `_build_template_xlsx()` fully implemented — Plan 06-02 only needs to wire it into the expander section

---
*Phase: 06-demo-first-ui*
*Completed: 2026-03-11*

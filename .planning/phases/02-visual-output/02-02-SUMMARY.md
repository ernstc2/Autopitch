---
phase: 02-visual-output
plan: "02"
subsystem: charts
tags: [matplotlib, numpy, pillow, png, bytesio, bar-chart, line-chart, waterfall-chart, kpi-scorecard]

# Dependency graph
requires:
  - phase: 02-visual-output plan 01
    provides: theme.py with NAVY_HEX, TEAL_HEX, LIGHT_GRAY_HEX, DARK_GRAY_HEX, POSITIVE_HEX, NEGATIVE_HEX, FONT_HEADING, FONT_BODY
provides:
  - autopitch/charts.py with bar_chart, line_chart, waterfall_chart, kpi_scorecard — all returning io.BytesIO PNG at 150 DPI
  - Agg backend configured for headless/server rendering
  - Consulting-style chart aesthetics (Big 4 color palette, Calibri/Arial font cascade, clean spines)
affects: [02-visual-output plan 03 (deck.py embeds these BytesIO images via add_picture)]

# Tech tracking
tech-stack:
  added: []  # matplotlib + numpy already installed in plan 02-01
  patterns:
    - "_to_bytesio(fig): savefig at DPI=150, buf.seek(0), plt.close(fig) — canonical headless chart-to-PPTX pattern"
    - "matplotlib.use('Agg') as first two lines before pyplot import — prevents GUI window in CLI/Streamlit"
    - "Waterfall as stacked bar: invisible bottom (running cumulative), visible colored bar floats at correct height"
    - "rcParams font cascade: ['Calibri', 'Arial', 'DejaVu Sans'] — graceful cross-platform font fallback"

key-files:
  created:
    - autopitch/charts.py
  modified: []

key-decisions:
  - "axhline() does not accept transform kwarg in matplotlib 3.10 — replaced with ax.plot() using transAxes for KPI separator lines"
  - "All chart functions use DPI=150 constant from module-level DPI variable — not hardcoded in each function"
  - "kpi_scorecard uses math.ceil for row count (ceiling division) to handle non-multiple-of-5 metric counts"

patterns-established:
  - "Pattern: All chart public functions follow (data..., title, ylabel?) -> io.BytesIO signature"
  - "Pattern: Private _apply_consulting_style(ax, fig) shared across bar/line/waterfall — single source of aesthetic config"
  - "Pattern: Private _to_bytesio(fig) encapsulates save+seek+close — prevents cursor-position silent failures"

requirements-completed: [CHRT-01, CHRT-02, CHRT-03, CHRT-04, CHRT-05]

# Metrics
duration: 2min
completed: 2026-03-10
---

# Phase 2 Plan 02: Charts Implementation Summary

**matplotlib chart module (bar, line, waterfall, KPI scorecard) returning io.BytesIO PNG at 150 DPI with Big 4 consulting aesthetics**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-10T15:14:23Z
- **Completed:** 2026-03-10T15:16:13Z
- **Tasks:** 1 (TDD: implementation)
- **Files modified:** 1

## Accomplishments

- Implemented `autopitch/charts.py` with 4 public functions and 2 private helpers
- All 5 CHRT tests turned GREEN (CHRT-01 through CHRT-05)
- Full test suite: 27 passed, 8 skipped (deck stubs), 0 failures
- Agg backend set before pyplot import — no display window in any environment
- `plt.close(fig)` in `_to_bytesio` — prevents memory leak in long-running Streamlit sessions
- `buf.seek(0)` before return — prevents silent empty-image failures in `add_picture()`

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement autopitch/charts.py** - `b757d2a` (feat)

## Files Created/Modified

- `autopitch/charts.py` — bar_chart, line_chart, waterfall_chart, kpi_scorecard with consulting-style aesthetics

## Decisions Made

- `axhline()` does not accept a `transform` keyword argument in matplotlib 3.10 (raises ValueError). Replaced with `ax.plot()` using `transform=ax.transAxes` for the KPI separator lines — this is the correct matplotlib 3.10 pattern for axes-coordinate line drawing.
- `_to_bytesio()` uses a single shared helper to enforce DPI=150, buf.seek(0), and plt.close(fig) — avoids copy-paste mistakes across 4 chart functions.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] matplotlib 3.10 axhline() incompatible with transform kwarg**
- **Found during:** Task 1 (kpi_scorecard implementation)
- **Issue:** The research file pattern uses `ax.axhline(..., transform=ax.transAxes)` but matplotlib 3.10 raises `ValueError: 'transform' is not allowed as a keyword argument; axhline generates its own transform`
- **Fix:** Replaced `axhline()` call with `ax.plot([x0, x1], [y, y], transform=ax.transAxes, ...)` which correctly accepts a transform in axes coordinates
- **Files modified:** `autopitch/charts.py`
- **Verification:** `pytest tests/test_charts.py::test_kpi_scorecard` passes GREEN
- **Committed in:** b757d2a (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug in research-provided code pattern)
**Impact on plan:** Single auto-fix necessary for correctness. No scope creep.

## Issues Encountered

None beyond the matplotlib 3.10 API incompatibility documented above as a deviation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `autopitch/charts.py` is complete and tested — deck.py (plan 02-03) can call `bar_chart`, `line_chart`, `waterfall_chart`, `kpi_scorecard` and embed the returned BytesIO directly via `slide.shapes.add_picture(buf, ...)`
- All 4 chart functions follow the same BytesIO pattern; deck.py import line: `from autopitch.charts import bar_chart, line_chart, waterfall_chart, kpi_scorecard`
- 8 deck test stubs in `tests/test_deck.py` are currently skipped and will activate when `autopitch/deck.py` is created in plan 02-03

---
*Phase: 02-visual-output*
*Completed: 2026-03-10*

---
phase: 02-visual-output
plan: "04"
subsystem: ui
tags: [pptx, python-pptx, matplotlib, visual-qa, deck]

# Dependency graph
requires:
  - phase: 02-visual-output
    plan: "03"
    provides: build_deck() generating 11-slide PPTX from FinancialData + MetricsOutput
provides:
  - Human-approved 11-slide Apple Financial Performance deck (output/apple_demo.pptx)
  - Two visual defect fixes: N/M display for negative-equity metrics, footer flush to bottom edge
  - Phase 2 quality gate passed — deck confirmed boardroom-ready
affects: [03-narrative, 04-api]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - autopitch/deck.py
    - autopitch/theme.py

key-decisions:
  - "N/M (not meaningful) used instead of N/A for D/E ratio and ROE when equity is negative — N/A implies missing data; N/M accurately signals the ratio is undefined due to negative equity"
  - "FOOTER_TOP derived from SLIDE_H (slide height constant) rather than a hardcoded offset — ensures footer always flushes to the physical bottom edge regardless of slide dimensions"

patterns-established:
  - "Visual QA gate: regenerate deck from demo data, human reviews in PowerPoint/LibreOffice, explicit approval required before phase closes"
  - "Negative-equity guard: any ratio computed over equity should render N/M when equity <= 0, not crash or display N/A"

requirements-completed: [CHRT-03, CHRT-04, DECK-01, DECK-02, DECK-03, DECK-04, DECK-05, DECK-06, DECK-07, DECK-08]

# Metrics
duration: 10min
completed: 2026-03-10
---

# Phase 2 Plan 04: Visual Inspection Summary

**Human-approved 11-slide Apple Financial Performance deck with two visual defect fixes applied during review: N/M for negative-equity ratios, and footer flushed to bottom edge via SLIDE_H-derived constant**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-10T15:24:00Z
- **Completed:** 2026-03-10T15:37:09Z
- **Tasks:** 2 (Task 1: regenerate deck; Task 2: human visual inspection — approved)
- **Files modified:** 2

## Accomplishments

- Regenerated output/apple_demo.pptx fresh from demo/apple_financials.xlsx with all 22 tests passing
- Human reviewer confirmed all 11 slides present, all charts rendering, Big 4 navy/teal/gray aesthetic professional
- Fixed two visual defects discovered during review before approval was granted
- Phase 2 quality gate passed — deck is boardroom-ready

## Task Commits

Each task was committed atomically:

1. **Task 1: Regenerate output/apple_demo.pptx from demo data** — no dedicated commit (deck file is not tracked in git; test suite passing was verified)
2. **Task 2: Visual inspection checkpoint (pre-approval fixes)**
   - `ce02de9` fix(02-04): use N/M (not meaningful) for D/E and ROE when equity is negative
   - `c80e820` fix(02-04): flush footer to bottom edge — FOOTER_TOP derived from SLIDE_H

## Files Created/Modified

- `autopitch/deck.py` — KPI scorecard now renders "N/M" for D/E ratio and ROE when equity is negative
- `autopitch/theme.py` — FOOTER_TOP constant changed to derive from SLIDE_H so footer sits at the physical bottom edge

## Decisions Made

- **N/M vs N/A for negative equity:** "N/A" implies data is absent; "N/M" (not meaningful) correctly signals the metric is defined but undefined in this financial context. Applied to D/E ratio and ROE.
- **FOOTER_TOP via SLIDE_H:** Hardcoded pixel offset placed footer above the true bottom edge. Deriving from the slide height constant makes it layout-invariant.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] KPI scorecard displayed "N/A" for D/E ratio and ROE on negative equity**
- **Found during:** Task 2 (visual inspection)
- **Issue:** When Apple's stockholders equity is negative (FY2023+), the KPI scorecard rendered "N/A" — misleading because it implies data is missing rather than the ratio being undefined
- **Fix:** Changed display string to "N/M" in deck.py KPI rendering block
- **Files modified:** autopitch/deck.py
- **Verification:** Human reviewer confirmed display after fix
- **Committed in:** ce02de9

**2. [Rule 1 - Bug] Footer was not flush to the bottom edge of slides**
- **Found during:** Task 2 (visual inspection)
- **Issue:** FOOTER_TOP was a hardcoded offset that placed the footer text slightly above the physical bottom edge, leaving a visible gap
- **Fix:** Derived FOOTER_TOP from SLIDE_H constant in theme.py so the footer always touches the slide bottom
- **Files modified:** autopitch/theme.py
- **Verification:** Human reviewer confirmed footer position after fix
- **Committed in:** c80e820

---

**Total deviations:** 2 auto-fixed (both Rule 1 — visual bugs caught during human QA)
**Impact on plan:** Both fixes were caught during the planned visual inspection step, not unplanned scope. No scope creep.

## Issues Encountered

None beyond the two visual defects above, which were caught and fixed within the same inspection session before approval.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 2 is fully complete. All 4 plans (02-01 through 02-04) are done, all requirements CHRT-01..05 and DECK-01..08 are satisfied.
- output/apple_demo.pptx is the reference artifact for Phase 3 (narrative/AI integration).
- Phase 3 will replace placeholder Executive Summary bullets with AI-generated text via the Anthropic SDK — see STATE.md blocker note about verifying current claude-sonnet model ID before coding.

---
*Phase: 02-visual-output*
*Completed: 2026-03-10*

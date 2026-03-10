---
phase: 03-ai-narrative
plan: 01
subsystem: api
tags: [anthropic, pydantic, claude, narrative, tdd]

# Dependency graph
requires:
  - phase: 01-data-foundation
    provides: FinancialData, MetricsOutput, StatementData Pydantic models
  - phase: 02-visual-output
    provides: deck.py consuming placeholder narrative strings

provides:
  - NarrativeOutput Pydantic v2 frozen model with all slide title and bullet fields
  - generate_narrative(data, metrics) -> NarrativeOutput single-call Claude API function
  - SYSTEM_PROMPT with Big 4 consulting analyst persona and one-shot example (NARR-04)
  - _build_prompt(), _parse_response(), _placeholder_narrative() helpers
  - anthropic>=0.84.0 in requirements.txt

affects:
  - 03-ai-narrative/03-02 (deck.py integration consuming NarrativeOutput)
  - 04-web-ui (end-to-end narrative generation in request handler)

# Tech tracking
tech-stack:
  added:
    - anthropic>=0.84.0 (official Anthropic Python SDK)
  patterns:
    - TDD Red-Green: tests written first (ImportError RED), then implementation (GREEN)
    - Pre-flight env check: os.environ.get("ANTHROPIC_API_KEY") before SDK instantiation
    - Single-call structured JSON output: all metrics in one messages.create call
    - Pydantic frozen model as typed contract and fallback object
    - _parse_response() strips markdown fences then json.loads(); falls back to NarrativeOutput() on error

key-files:
  created:
    - autopitch/narrative.py
    - tests/test_narrative.py
  modified:
    - requirements.txt

key-decisions:
  - "generate_narrative() pre-flight checks os.environ.get('ANTHROPIC_API_KEY') — if absent returns NarrativeOutput() immediately, never instantiates SDK (NARR-05)"
  - "Single messages.create call per invocation: all MetricsOutput fields serialised into one user message (NARR-03)"
  - "Model string is exactly 'claude-sonnet-4-6' — verified against official docs 2026-03-10 (not legacy claude-3-sonnet)"
  - "NarrativeOutput has placeholder string defaults for every field — safe fallback without special-casing callers"
  - "_parse_response() handles markdown-fenced JSON by stripping fences before json.loads() — mitigates Pitfall 3"
  - "max_tokens=2048 chosen for comfortable headroom over ~600-token minimum output estimate"

patterns-established:
  - "Pattern: API module with pre-flight key guard returning typed placeholder object on absent key"
  - "Pattern: Single bulk API call over per-item calls — serialise all inputs, parse structured JSON output once"
  - "Pattern: TDD for external API modules — mock at the SDK class level (patch 'autopitch.narrative.Anthropic')"

requirements-completed: [NARR-01, NARR-02, NARR-03, NARR-05]

# Metrics
duration: 7min
completed: 2026-03-10
---

# Phase 3 Plan 01: Narrative Module Summary

**NarrativeOutput Pydantic model and generate_narrative() single-call Claude API function with pre-flight key guard and placeholder fallback, driven by TDD**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-03-10T18:13:17Z
- **Completed:** 2026-03-10T18:20:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Created `autopitch/narrative.py` with NarrativeOutput Pydantic v2 frozen model, generate_narrative(), SYSTEM_PROMPT (consulting analyst persona + one-shot example), _build_prompt(), _parse_response(), and _placeholder_narrative()
- All 4 unit tests GREEN: fallback (NARR-05), title population (NARR-01), bullet count (NARR-02), single API call (NARR-03)
- Full suite 39 tests pass, zero regressions across Phase 1 and Phase 2 tests

## Task Commits

Each task was committed atomically:

1. **Task 1: Write failing tests for narrative module (TDD Wave 0)** - `9699ad9` (test)
2. **Task 2: Implement narrative.py and install anthropic SDK** - `15593cc` (feat)

**Plan metadata:** _(docs commit follows)_

_Note: TDD tasks have two commits — RED test commit, then GREEN implementation commit_

## Files Created/Modified

- `autopitch/narrative.py` — NarrativeOutput model, generate_narrative(), SYSTEM_PROMPT, all helpers
- `tests/test_narrative.py` — 4 unit tests covering NARR-01, NARR-02, NARR-03, NARR-05
- `requirements.txt` — added anthropic>=0.84.0

## Decisions Made

- Pre-flight `os.environ.get("ANTHROPIC_API_KEY")` check before SDK instantiation prevents AuthenticationError from bubbling out of build_deck() in Phase 4. Returns `NarrativeOutput()` (all defaults) immediately if key absent.
- Single `messages.create()` call with all MetricsOutput data serialised once — satisfies NARR-03 and avoids 11x cost/latency of per-slide calls.
- Model string `"claude-sonnet-4-6"` hardcoded after verification against official docs (2026-03-10). Legacy `claude-3-sonnet` strings cause model_not_found errors.
- `NarrativeOutput` field defaults are meaningful placeholders (e.g., "Executive Summary", "P&L | Revenue Trends") so the deck renders legibly even without AI content.
- `_parse_response()` strips markdown fences before `json.loads()` to guard against model returning fenced JSON despite explicit "JSON only" instruction.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required for this plan. The ANTHROPIC_API_KEY environment variable is checked at runtime by generate_narrative(); if absent the function gracefully returns placeholder content.

## Next Phase Readiness

- `NarrativeOutput` and `generate_narrative` are importable and fully tested — ready for Plan 03-02 (deck.py integration)
- `build_deck()` in deck.py will accept an optional `NarrativeOutput` parameter; when None it defaults to `NarrativeOutput()` (all placeholders)
- anthropic SDK v0.84.0 installed and in requirements.txt

---
*Phase: 03-ai-narrative*
*Completed: 2026-03-10*

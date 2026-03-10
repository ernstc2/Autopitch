---
phase: 03-ai-narrative
verified: 2026-03-10T19:00:00Z
status: human_needed
score: 4/5 must-haves verified (automated); 5th truth requires human confirmation
re_verification: false
human_verification:
  - test: "Open output/ai_narrative_test.pptx and confirm slide headers are insight-first"
    expected: "Slide headers such as 'Revenue accelerated 18% — Services mix the primary driver' rather than 'P&L | Revenue Trends'"
    why_human: "Consulting voice quality and title insight-level cannot be verified programmatically; the test requires a real API call and human judgment about analytical depth"
  - test: "Confirm NARR-04 checkbox updated in REQUIREMENTS.md from [ ] to [x]"
    expected: "NARR-04 row shows [x] and Traceability table shows 'Complete'"
    why_human: "Documentation drift — implementation clearly satisfies NARR-04 but the requirements file was not updated post-implementation; human must confirm and update"
---

# Phase 3: AI Narrative Verification Report

**Phase Goal:** Every deck section carries Claude-generated insight-first titles and consulting-voice bullet commentary — with graceful fallback when no API key is present
**Verified:** 2026-03-10T19:00:00Z
**Status:** human_needed (all automated checks pass; two human confirmation items remain)
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | No API key → NarrativeOutput returned with non-empty placeholders, no exception | VERIFIED | `generate_narrative()` pre-flight guard at narrative.py:167–169; `test_fallback_no_api_key` GREEN |
| 2 | Mocked API call → NarrativeOutput fields match JSON response | VERIFIED | `test_narrative_titles_not_generic` GREEN; all 10 title fields asserted |
| 3 | Exactly one `messages.create()` call per invocation regardless of slide count | VERIFIED | Single call at narrative.py:172; `test_single_api_call` asserts `call_count == 1` |
| 4 | All 10 slide headers in deck.py use NarrativeOutput fields (not hard-coded strings) | VERIFIED | 14 `narrative.*` references in deck.py; no hard-coded header strings remain |
| 5 | Real API-generated titles read as analytical insights, not data labels | HUMAN NEEDED | SUMMARY documents human QA approved; cannot re-verify programmatically without live API call |

**Score:** 4/5 automated truths verified; truth 5 documented as human-approved in 03-02-SUMMARY.md

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `autopitch/narrative.py` | NarrativeOutput model, generate_narrative(), SYSTEM_PROMPT, _build_prompt(), _parse_response(), _placeholder_narrative() | VERIFIED | 179 lines; all six exports present and substantive |
| `tests/test_narrative.py` | 4 pytest tests covering NARR-01, NARR-02, NARR-03, NARR-05 | VERIFIED | 4 tests, all GREEN (39/39 suite passes) |
| `requirements.txt` | `anthropic>=0.84.0` dependency | VERIFIED | Line 1: `anthropic>=0.84.0` present |
| `autopitch/deck.py` | build_deck() with optional `narrative: NarrativeOutput | None = None` | VERIFIED | Signature at deck.py:139–143; 10 slide headers wired to narrative fields |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `tests/test_narrative.py` | `autopitch/narrative.py` | `patch('autopitch.narrative.Anthropic')` | WIRED | mock_client.messages.create patched and asserted in all 3 API-path tests |
| `autopitch/narrative.py` | `anthropic.Anthropic` | `os.environ.get('ANTHROPIC_API_KEY')` pre-flight | WIRED | narrative.py:167: `api_key = os.environ.get("ANTHROPIC_API_KEY")` — absent returns early |
| `autopitch/deck.py` | `autopitch.narrative.NarrativeOutput` | `from autopitch.narrative import NarrativeOutput` | WIRED | deck.py:21; narrative parameter wired at 14 call sites |
| `build_deck() header calls` | `narrative.*_title` and `narrative.*_bullets` fields | `_add_header(slide, narrative.X_title)` | WIRED | All 10 slide headers use narrative fields (deck.py:405–492); exec summary bullets at line 406; pl_bullets at 424; bs_bullets at 453; cf_bullets at 482 |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| NARR-01 | 03-01, 03-02 | Insight-first slide titles via Claude API | SATISFIED | NarrativeOutput title fields populated from API response; all 10 deck headers wired to narrative fields; test_narrative_titles_not_generic GREEN |
| NARR-02 | 03-01, 03-02 | 2-3 bullet narrative commentary per deck section via Claude API | SATISFIED | pl_bullets, bs_bullets, cf_bullets wired into slide_pl_margin, slide_bs_wc, slide_cf_trend; test_narrative_bullets_count asserts len >= 2 per section |
| NARR-03 | 03-01 | Single Claude API call per deck run | SATISFIED | One `client.messages.create()` call at narrative.py:172; test_single_api_call asserts call_count == 1 |
| NARR-04 | 03-02 | System prompt and one-shot example enforce consulting voice | SATISFIED (implementation) / DOCUMENTATION DRIFT | SYSTEM_PROMPT at narrative.py:64–84 contains Big 4 consulting persona, forward-looking bullet rules, no-filler-phrase rule, and XML `<example>` one-shot block with sample JSON output. Implementation satisfies the requirement. HOWEVER: REQUIREMENTS.md still shows `[ ] NARR-04` (Pending) and Traceability table shows "Pending". Documentation was not updated after 03-02-SUMMARY marked it complete. |
| NARR-05 | 03-01 | Graceful fallback to placeholder commentary when API key absent | SATISFIED | Pre-flight guard at narrative.py:167–169 returns NarrativeOutput() immediately; test_fallback_no_api_key GREEN |

**Orphaned requirements:** None. All 5 NARR-* requirements are claimed by plans and verified above.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `.planning/REQUIREMENTS.md` | 48, 119 | NARR-04 marked `[ ]` Pending but implementation complete | Warning | Documentation drift only — no code impact. REQUIREMENTS.md checkbox and Traceability row need updating from Pending to Complete. |

No code-level anti-patterns found:
- No TODO/FIXME/HACK comments in narrative.py or deck.py
- No stub implementations (return null / return {} / empty handlers)
- No per-slide API call loop
- All "placeholder" references are intentional fallback behavior, not incomplete code

---

## Human Verification Required

### 1. Consulting Voice Quality (NARR-01/NARR-04)

**Test:** With `ANTHROPIC_API_KEY` set, run the smoke test from 03-02-PLAN.md Task 2 and open the generated PPTX.
**Expected:** Slide 2 header reads as analytical insight (e.g., "Revenue grew X% — Services mix the primary driver"), not a data label ("Executive Summary"). Slide 4, 7, 10 headers similarly analytical. Bullet commentary visible below charts on those slides.
**Why human:** Consulting voice quality, analytical depth, and insight-first framing require human judgment — cannot be verified by string matching.

### 2. REQUIREMENTS.md Documentation Update (NARR-04)

**Test:** Open `.planning/REQUIREMENTS.md` and update NARR-04 from `[ ]` to `[x]` and the Traceability table from `Pending` to `Complete`.
**Expected:** NARR-04 entry reads `- [x] **NARR-04**: System prompt and one-shot example enforce consulting-voice output...` and Traceability row shows `Complete`.
**Why human:** This is a documentation correction requiring a deliberate human edit and commit — not automated code verification.

---

## Summary

Phase 3 goal achievement is **substantively complete**. Every automated truth passes:

- `autopitch/narrative.py` is fully implemented — NarrativeOutput Pydantic model, SYSTEM_PROMPT with Big 4 consulting persona and one-shot example, single-call `generate_narrative()`, pre-flight API key guard, and `_parse_response()` with markdown-fence stripping.
- `autopitch/deck.py` is fully wired — all 10 slide headers use `narrative.*_title` fields; exec summary, P&L margin, Balance Sheet WC, and Cash Flow trend slides show `narrative.*_bullets` commentary; backwards-compatible with `build_deck(data, metrics)` callers.
- 39/39 tests pass with zero regressions.
- Requirements NARR-01 through NARR-05 are all satisfied in code.

The only open item is documentation drift: REQUIREMENTS.md shows NARR-04 as `[ ] Pending` despite its implementation being complete in commit `15593cc` (SYSTEM_PROMPT) and confirmed by 03-02-SUMMARY. This should be corrected before Phase 4 begins.

Human QA approval is documented in 03-02-SUMMARY.md ("Human QA approved: real API-generated titles confirmed as analytical insights") but cannot be re-verified programmatically here.

---

_Verified: 2026-03-10T19:00:00Z_
_Verifier: Claude (gsd-verifier)_

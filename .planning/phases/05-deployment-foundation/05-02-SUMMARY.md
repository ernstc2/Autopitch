---
phase: 05-deployment-foundation
plan: 02
subsystem: infra
tags: [streamlit-cloud, github, deployment, anthropic-api]

# Dependency graph
requires:
  - phase: 05-01
    provides: Fixed requirements.txt, working app.py, Streamlit secrets config
provides:
  - Live public Streamlit Cloud URL for the Autopitch app
  - GitHub remote fully synced (all commits + v1.0 tag pushed)
  - End-to-end PPTX generation verified on Cloud with real Claude narrative
affects:
  - 06-ui-polish
  - 07-demo-hardening

# Tech tracking
tech-stack:
  added: [streamlit-cloud]
  patterns: [repo-linked auto-deploy from GitHub main branch, ANTHROPIC_API_KEY as TOML secret auto-promoted to os.environ]

key-files:
  created: []
  modified: []

key-decisions:
  - "Streamlit Cloud URL: https://autopitch-54x3pzywhwscvrs9jw6yx7.streamlit.app/ — user-facing canonical demo link"
  - "Python 3.11 selected in Advanced Settings on first deploy — cannot change without full redeployment"
  - "ANTHROPIC_API_KEY injected as Streamlit TOML secret; auto-promoted to os.environ so narrative.py requires zero code changes"

patterns-established:
  - "GitHub push unblocked via gh auth login — PAT rotation approach for future pushes"
  - "Streamlit Cloud secrets stored as root-level TOML key (not nested under [section])"

requirements-completed: [DEPL-03]

# Metrics
duration: ~45min
completed: 2026-03-11
---

# Phase 5 Plan 02: Deploy to Streamlit Cloud Summary

**Autopitch deployed publicly at https://autopitch-54x3pzywhwscvrs9jw6yx7.streamlit.app/ with real Claude narrative generation, Excel upload, and one-click PPTX download verified end-to-end**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-03-11
- **Completed:** 2026-03-11
- **Tasks:** 3
- **Files modified:** 0 (deployment-only plan — no code changes)

## Accomplishments

- All local commits pushed to GitHub origin/main; v1.0 tag successfully pushed to remote (resolving the 403 auth blocker from v1.0 milestone)
- App deployed on Streamlit Community Cloud with Python 3.11 and ANTHROPIC_API_KEY secret configured
- User verified upload of demo/apple_financials.xlsx produces a downloadable PPTX with real Claude-generated narrative (not placeholders)

## Task Commits

This plan was deployment-only — no new code commits were required. Tasks were executed via manual browser configuration and command-line git push.

1. **Task 1: Push to GitHub** — git push origin main + git push origin v1.0 (auth resolved via gh auth login)
2. **Task 2: Deploy on Streamlit Cloud** — Manual browser deployment via share.streamlit.io dashboard
3. **Task 3: Verify end-to-end on Cloud** — User approved: upload works, Claude narrative generates, PPTX downloads

## Files Created/Modified

None — this plan contained zero code changes. All deployment configuration was done via the Streamlit Cloud dashboard (secrets, Python version, repo connection).

## Decisions Made

- **Canonical public URL:** https://autopitch-54x3pzywhwscvrs9jw6yx7.streamlit.app/ — this is the demo link to share
- **Python 3.11 locked in** via Advanced Settings on first deploy; changing later requires full redeployment
- **Secrets approach confirmed:** ANTHROPIC_API_KEY as a root-level TOML key in Streamlit secrets is auto-promoted to `os.environ` — no code changes needed in `narrative.py`

## Deviations from Plan

None — plan executed exactly as written. The GitHub auth blocker (403 on tag push) was a known pre-condition already documented in the plan's `user_setup` section.

## Issues Encountered

- GitHub 403 on `git push origin v1.0` was a pre-existing known issue from v1.0 milestone. Resolved during Task 1 via `gh auth login` re-authentication.

## User Setup Required

All user setup was completed during execution:

- GitHub auth re-established via `gh auth login`
- Streamlit Cloud connected to GitHub repo, Python 3.11 selected, ANTHROPIC_API_KEY secret added
- App rebooted after secrets configuration

No further external service configuration is required for Phase 6 or 7.

## Next Phase Readiness

- **Phase 6 (UI Polish):** App is live and publicly accessible — any UI changes pushed to GitHub main will auto-deploy via Streamlit Cloud
- **Phase 7 (Demo Hardening):** End-to-end generation confirmed working; hardening can focus on edge cases and error states
- No blockers. Deployment foundation is complete.

---
*Phase: 05-deployment-foundation*
*Completed: 2026-03-11*

---
phase: 05-deployment-foundation
plan: 01
subsystem: infra
tags: [requirements, streamlit, secrets, gitignore, pytest, python-pptx, matplotlib]

requires: []
provides:
  - "requirements.txt with 7 runtime-only deps (python-pptx, matplotlib, openpyxl, anthropic, pydantic, python-dotenv, streamlit)"
  - "requirements-dev.txt with -r requirements.txt + pytest/pytest-cov for CI"
  - ".streamlit/secrets.toml gitignored with ANTHROPIC_API_KEY placeholder"
  - ".env.example updated to reference secrets.toml for Streamlit Cloud"
  - "tests/test_requirements.py — automated DEPL-01 verification"
  - "tests/test_deployment.py — automated DEPL-02 verification"
affects: [06-ui-polish, 07-demo-hardening]

tech-stack:
  added: [requirements-dev.txt pattern, .streamlit/secrets.toml]
  patterns: ["Runtime/dev dependency split via requirements.txt + requirements-dev.txt", "Streamlit secrets via .streamlit/secrets.toml (root-level keys auto-promoted to os.environ)"]

key-files:
  created:
    - requirements-dev.txt
    - .streamlit/secrets.toml
    - tests/test_requirements.py
    - tests/test_deployment.py
  modified:
    - requirements.txt
    - .gitignore
    - .env.example

key-decisions:
  - "Split runtime and dev deps: requirements.txt has 7 runtime-only packages; requirements-dev.txt adds pytest/pytest-cov via -r include"
  - "gitignore .streamlit/secrets.toml before creating the file — prevents accidental commit"
  - "Root-level TOML key ANTHROPIC_API_KEY is auto-promoted to os.environ on Streamlit Cloud — no code changes needed"

patterns-established:
  - "Dependency split: requirements.txt = runtime, requirements-dev.txt = test tools"
  - "Secrets management: .env for CLI, .streamlit/secrets.toml for Streamlit (both gitignored)"

requirements-completed: [DEPL-01, DEPL-02]

duration: 4min
completed: 2026-03-11
---

# Phase 5 Plan 1: Deployment Foundation Summary

**Removed pytest/pytest-cov from prod deps, added missing python-pptx and matplotlib, split into runtime+dev requirement files, and gitignored .streamlit/secrets.toml with ANTHROPIC_API_KEY placeholder**

## Performance

- **Duration:** ~4 min
- **Started:** 2026-03-11T00:41:12Z
- **Completed:** 2026-03-11T00:44:34Z
- **Tasks:** 2 (TDD: RED then GREEN)
- **Files modified:** 6

## Accomplishments

- requirements.txt now has exactly 7 runtime deps — Streamlit Cloud builds will succeed with python-pptx and matplotlib present
- requirements-dev.txt created with -r include pattern so CI installs everything with one file
- .streamlit/secrets.toml gitignored before creation, with ANTHROPIC_API_KEY placeholder for local development
- 14 new automated tests across test_requirements.py and test_deployment.py verify all DEPL-01 and DEPL-02 conditions
- Full test suite: 62 tests passing (was 48 before this plan)

## Task Commits

Each task was committed atomically:

1. **Task 1: Write deployment verification tests (RED)** - `c9cb0d3` (test)
2. **Task 2: Fix dependencies, configure secrets, make tests green (GREEN)** - `86efe14` (feat)

## Files Created/Modified

- `requirements.txt` — rewritten with 7 runtime-only deps (alphabetical, >= floors); added python-pptx, matplotlib; removed pytest, pytest-cov
- `requirements-dev.txt` — new file; -r requirements.txt + pytest>=8.0.0 + pytest-cov>=5.0.0
- `.gitignore` — added `.streamlit/secrets.toml` under `# Streamlit secrets` comment
- `.env.example` — added secrets.toml comment block for Streamlit Cloud users
- `.streamlit/secrets.toml` — new gitignored file; root-level ANTHROPIC_API_KEY placeholder
- `tests/test_requirements.py` — 12 tests for DEPL-01 (runtime inclusions + pytest exclusions + dev file structure)
- `tests/test_deployment.py` — 2 tests for DEPL-02 (gitignore entry + git ls-files check)

## Decisions Made

- gitignore entry added before file creation — prevents race condition where file is created tracked
- root-level TOML key format chosen (vs `[secrets]` table) — Streamlit Cloud auto-promotes root-level keys to os.environ, requiring zero code changes in narrative.py

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

For local development: populate `.streamlit/secrets.toml` with your real key:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

For Streamlit Cloud deployment: configure via App Settings > Secrets in the dashboard (paste the TOML directly).

## Next Phase Readiness

- Deployment blockers resolved — Streamlit Cloud build will succeed
- requirements-dev.txt ready for CI pipeline configuration
- Phase 6 (UI Polish) and Phase 7 (Demo Hardening) can proceed

---
*Phase: 05-deployment-foundation*
*Completed: 2026-03-11*

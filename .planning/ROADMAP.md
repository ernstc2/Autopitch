# Roadmap: Autopitch

## Overview

Autopitch transforms a single Excel workbook into a boardroom-ready consulting deck. The v1.0 pipeline is complete and ships all core features. The v1.1 milestone transforms the bare Streamlit UI into a portfolio-ready live demo: deployed on Streamlit Cloud, demo-first UX for visitors who arrive without data, skills showcase for recruiters, and visual polish befitting a finished product.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-03-10)
- 🚧 **v1.1 Portfolio Demo Polish** — Phases 5-7 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) — SHIPPED 2026-03-10</summary>

- [x] Phase 1: Data Foundation (4/4 plans) — completed 2026-03-10
- [x] Phase 2: Visual Output (4/4 plans) — completed 2026-03-10
- [x] Phase 3: AI Narrative (2/2 plans) — completed 2026-03-10
- [x] Phase 4: Interfaces and Polish (3/3 plans) — completed 2026-03-10

See: `.planning/milestones/v1.0-ROADMAP.md` for full phase details.

</details>

### 🚧 v1.1 Portfolio Demo Polish (In Progress)

**Milestone Goal:** Transform the Streamlit UI into a portfolio-ready live demo that showcases capabilities, technical skills, and guides visitors through the experience. Accessible via a public Streamlit Cloud URL.

- [ ] **Phase 5: Deployment Foundation** - Fix confirmed deployment blockers and get the app live on Streamlit Cloud
- [x] **Phase 6: Demo-First UI** - Build the complete four-section portfolio UI in app.py (completed 2026-03-11)
- [x] **Phase 7: Polish and Keep-Alive** - Visual theme, generation stats, and hibernation prevention (completed 2026-03-11)

## Phase Details

### Phase 5: Deployment Foundation
**Goal**: The app builds and runs correctly on Streamlit Cloud with all runtime dependencies present and secrets managed securely
**Depends on**: Phase 4 (v1.0 complete)
**Requirements**: DEPL-01, DEPL-02, DEPL-03
**Success Criteria** (what must be TRUE):
  1. Running `pip install -r requirements.txt` installs all packages needed to generate a deck (including python-pptx and matplotlib); pytest and pytest-cov are absent from this file
  2. The local app starts and generates a deck successfully using ANTHROPIC_API_KEY loaded from `.streamlit/secrets.toml` (not .env)
  3. The app is deployed and reachable at a public Streamlit Cloud URL with Claude narrative generation working end-to-end
**Plans**: 2 plans

Plans:
- [ ] 05-01: Fix requirements.txt, create requirements-dev.txt, configure secrets
- [ ] 05-02: Deploy to Streamlit Cloud and verify end-to-end

### Phase 6: Demo-First UI
**Goal**: A portfolio visitor who arrives at the live URL with no data can click one button and see a generated consulting deck, then optionally upload their own data — and the page clearly communicates what the tool does and how it was built
**Depends on**: Phase 5
**Requirements**: DEMO-01, DEMO-02, DEMO-03, DEMO-04, UPLD-01, UPLD-02, UPLD-03, SKIL-01
**Success Criteria** (what must be TRUE):
  1. A visitor landing on the app sees a hero section explaining what Autopitch does before encountering any interactive element
  2. Clicking "Try the Demo" generates a deck from bundled Apple data and presents a download button; clicking the download button does not make the button disappear
  3. After demo generation, elapsed time and slide count are displayed next to the download button
  4. A visitor can upload their own Excel file using clearly labeled instructions, an expandable format guide showing required sheets and columns, and a downloadable Excel template
  5. A tech stack section shows 5-6 technologies as badges with one-sentence architectural rationale per tool
**Plans**: 2 plans

Plans:
- [ ] 06-01: Hero section, session state wiring, one-click demo with download and generation stats
- [ ] 06-02: Upload section with format guide, template download, and tech stack showcase

### Phase 7: Polish and Keep-Alive
**Goal**: The deployed app looks polished and remains accessible to portfolio visitors around the clock without requiring manual intervention
**Depends on**: Phase 6
**Requirements**: VISL-01, VISL-02, DEPL-04
**Success Criteria** (what must be TRUE):
  1. The app loads with the navy color palette and wide layout applied — no default Streamlit salmon/pink theme visible
  2. Column widths, section spacing, and header copy are visually balanced — the page reads as a finished product, not a prototype
  3. A GitHub Actions workflow runs every 6 hours and pings the live app URL, preventing the app from hibernating between portfolio visits
**Plans**: 2 plans

Plans:
- [ ] 07-01: Streamlit theme config.toml and layout polish pass
- [ ] 07-02: GitHub Actions keep-alive workflow

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Data Foundation | v1.0 | 4/4 | Complete | 2026-03-10 |
| 2. Visual Output | v1.0 | 4/4 | Complete | 2026-03-10 |
| 3. AI Narrative | v1.0 | 2/2 | Complete | 2026-03-10 |
| 4. Interfaces and Polish | v1.0 | 3/3 | Complete | 2026-03-10 |
| 5. Deployment Foundation | v1.1 | 2/2 | Complete | 2026-03-11 |
| 6. Demo-First UI | 2/2 | Complete   | 2026-03-11 | - |
| 7. Polish and Keep-Alive | 2/2 | Complete   | 2026-03-11 | - |

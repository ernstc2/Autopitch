# Requirements: Autopitch v1.1

**Defined:** 2026-03-10
**Core Value:** User uploads one Excel file and gets back a boardroom-ready consulting deck in seconds

## v1.1 Requirements

Requirements for Portfolio Demo Polish milestone. Each maps to roadmap phases.

### Deployment Infrastructure

- [x] **DEPL-01**: App has correct `requirements.txt` with all runtime dependencies (python-pptx, matplotlib) and dev deps split to `requirements-dev.txt`
- [x] **DEPL-02**: Secrets management configured — `.streamlit/secrets.toml` gitignored, API key injected via Streamlit Cloud dashboard
- [x] **DEPL-03**: App deployed and running on Streamlit Community Cloud with working Claude narrative generation
- [ ] **DEPL-04**: GitHub Actions keep-alive cron pings app every 6h to prevent hibernation

### Demo Experience

- [x] **DEMO-01**: Hero/landing section explains what Autopitch does before any interactive elements
- [x] **DEMO-02**: One-click "Try the Demo" button generates a deck from bundled Apple data with no user input required
- [x] **DEMO-03**: Generated deck bytes persist across reruns via `st.session_state` so download button doesn't disappear
- [x] **DEMO-04**: Generation stats displayed after deck creation (elapsed time, slide count)

### Upload Path

- [ ] **UPLD-01**: File uploader section with clear instructions for uploading custom Excel data
- [ ] **UPLD-02**: In-app format guide (expandable accordion) showing required sheet names, column structure, and example values
- [ ] **UPLD-03**: Downloadable Excel template with correct MIME type and binary handling

### Skills Showcase

- [ ] **SKIL-01**: Tech stack section displaying 5-6 key technologies as badges with one-line rationale per tool

### Visual Polish

- [ ] **VISL-01**: Streamlit theme configured via `.streamlit/config.toml` (navy palette, wide layout, sans-serif font)
- [ ] **VISL-02**: Polished layout with proper column widths, spacing, section headers, and copy

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Features

- **ADV-01**: Multi-company comparison decks
- **ADV-02**: Real-time SEC/Yahoo Finance data ingestion
- **ADV-03**: In-app slide preview (PPTX rendered as images)
- **ADV-04**: PDF export option

## Out of Scope

| Feature | Reason |
|---------|--------|
| Per-slide progress bar | `run_pipeline()` is a single blocking call; faking progress is misleading |
| User accounts / saved decks | Auth infrastructure out of scope; stateless is correct for portfolio demo |
| Always-on ping loop hack | Against Streamlit fair-use intent; GitHub Actions cron is the correct approach |
| Custom branding / white-labeling | One polished template is the goal |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DEPL-01 | Phase 5 | Complete |
| DEPL-02 | Phase 5 | Complete |
| DEPL-03 | Phase 5 | Complete |
| DEPL-04 | Phase 7 | Pending |
| DEMO-01 | Phase 6 | Complete |
| DEMO-02 | Phase 6 | Complete |
| DEMO-03 | Phase 6 | Complete |
| DEMO-04 | Phase 6 | Complete |
| UPLD-01 | Phase 6 | Pending |
| UPLD-02 | Phase 6 | Pending |
| UPLD-03 | Phase 6 | Pending |
| SKIL-01 | Phase 6 | Pending |
| VISL-01 | Phase 7 | Pending |
| VISL-02 | Phase 7 | Pending |

**Coverage:**
- v1.1 requirements: 14 total
- Mapped to phases: 14
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-10*
*Last updated: 2026-03-10 after roadmap creation*

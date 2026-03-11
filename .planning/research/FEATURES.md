# Feature Research

**Domain:** Portfolio demo UI — Streamlit app for a data/finance Python tool targeting Big 4 tech consulting recruiters
**Researched:** 2026-03-10
**Confidence:** HIGH (Streamlit docs verified) / MEDIUM (UX patterns from community evidence)
**Scope:** v1.1 only — new features not yet built. v1.0 capabilities are dependencies, not scope.

---

## Existing Capabilities (v1.0 Dependencies)

Already built. All v1.1 features compose on top of these.

- `run_pipeline(file_like) -> bytes` — full Excel-to-PPTX pipeline
- `app.py` — bare Streamlit file uploader (no hero, no demo mode, no instructions)
- `demo/apple_financials.xlsx` — bundled Apple FY2020-2024 data committed to repo
- Graceful fallback when `ANTHROPIC_API_KEY` absent (placeholder narrative, no crash)
- `ValidationError` caught and displayed as `st.error` string

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features a portfolio visitor expects. Missing any of these and the app feels broken or untrustworthy.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Hero / landing section | Every polished demo app explains itself before asking for input; raw file uploader as first element reads as unfinished | LOW | `st.title`, `st.subheader`, 2-3 sentence tool pitch, then action buttons |
| One-click Apple demo button | Visitors will not upload their own data first; proof of output must come before any ask | LOW | `open("demo/apple_financials.xlsx", "rb")` wrapped in BytesIO; call `run_pipeline()` |
| Download button wired to demo output | A demo that doesn't produce a downloadable artifact proves nothing | LOW | Same `st.download_button` already used on upload path; replicate for demo path |
| Loading spinner during generation | Deck generation takes 5-15s with Claude API; silence reads as frozen | LOW | Already on upload path via `st.spinner`; apply to demo path too |
| Friendly error handling | A Python traceback on bad input loses recruiter trust immediately | LOW | Already catching `ValidationError`; add a general `except Exception` with a human-readable fallback |
| Live deployed URL (not localhost) | Recruiters will not run `pip install`; the app must be reachable at a shareable link | MEDIUM | Streamlit Community Cloud — public GitHub repo required, `ANTHROPIC_API_KEY` via TOML secrets |
| `requirements.txt` accurate and committed | Streamlit Cloud builds the environment from this file; missing or wrong pins = deploy failure | LOW | Verify all transitive deps; pin major versions at minimum |

### Differentiators (Competitive Advantage)

Features that distinguish this from a generic Streamlit file-uploader tutorial.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Tech stack / skills section | Recruiters scan for Python, Claude API, Pydantic, PPTX generation keywords; surfacing them in the UI itself signals intent, not just competence | LOW | `st.expander` or sidebar; plain list of technologies with one-line descriptions each |
| Upload-your-own-data path with guided instructions | Shows the tool generalises beyond one canned example; makes the demo credible as a real tool | MEDIUM | Accordion showing required sheet names, column headers, and data types; mirrors TEMPLATE_FORMAT.md |
| Downloadable Excel template | Removes the "I don't know the format" barrier; a visitor who successfully uses their own data is the strongest possible demo signal | LOW | Serve `demo/apple_financials.xlsx` (already formatted correctly) or a stripped blank via `st.download_button` |
| Generation stats (elapsed time + slide count) | Grounds the demo claim with observable evidence; "12 slides in 8 seconds" is more convincing than any marketing copy | LOW | `time.time()` wrapper; show elapsed seconds and output slide count after `run_pipeline()` returns |
| Polished visual hierarchy | Layout quality signals production thinking vs notebook dump; recruiter impression formed in first 3 seconds | LOW-MEDIUM | `st.columns` for two-column layouts, consistent section headers, no raw `st.write` clutter |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Always-on / no-sleep hack (GitHub Actions ping loop) | Free tier sleeps after ~12h inactivity; 20-30s cold start feels broken to a recruiter | Fragile; against Streamlit Community Cloud fair-use intent; can get app suspended | Accept the cold start; `st.info` callout explaining the app may take a moment to wake is honest and sufficient |
| Inline data validation UI with error tables | Detailed feedback on bad uploads looks user-friendly | Scope creep — a proper validation UI is a separate project; existing `ValidationError` string message is appropriate for v1.1 | Keep the error string; add a "check your file matches the template" note linking to instructions |
| Per-slide progress bar | Demonstrates technical depth | `run_pipeline()` is a single blocking call; faking progress with `st.progress` polling is misleading and adds complexity with no real signal | Single spinner + elapsed time on completion is honest |
| In-app slide preview (render PPTX as images) | Visually impressive | Requires `python-pptx` → PIL conversion per slide; heavy, slow, fragile on Cloud free tier RAM limits | PPTX download IS the deliverable; open in PowerPoint is the correct viewing experience |
| Multiple file upload / batch mode | Power-user feature | Multiplies API cost on a shared Cloud deployment; single-file focus is the portfolio story | One file at a time; note extensibility in README |
| User accounts / saved decks | Makes it feel like a real product | Requires auth infrastructure entirely out of scope; Streamlit Community Cloud is inherently stateless | Each session generates fresh; no persistence needed |

---

## Feature Dependencies

```
[Deployed URL]
    └──requires──> [Public GitHub repo]
    └──requires──> [requirements.txt accurate + committed]
    └──requires──> [ANTHROPIC_API_KEY in Streamlit Cloud secrets TOML]
    └──note: load_dotenv() is a no-op on Cloud; os.environ populated by Cloud secrets

[One-click Apple demo]
    └──requires──> [demo/apple_financials.xlsx committed to repo]
    └──lives in──> [Hero / landing section]

[Demo download button]
    └──requires──> [One-click Apple demo] (needs the bytes output)

[Upload-your-own guided path]
    └──requires──> [In-app format instructions accordion]
    └──enhances──> [Downloadable Excel template]  (template + instructions are a pair)

[Tech stack / skills section]
    └──independent──> all other features  (pure UI content, no logic dependency)

[Generation stats]
    └──requires──> [One-click Apple demo] or [upload path]  (wraps run_pipeline call)

[Visual hierarchy polish]
    └──enhances──> all UI features  (applied last after structure is locked)
```

### Dependency Notes

- **Public repo is a hard blocker for Cloud deployment.** The Autopitch repo currently has push auth issues (403 on tag push noted in MEMORY.md). GitHub auth must be re-established before any Cloud deployment task begins.
- **`load_dotenv()` does nothing on Streamlit Cloud.** The existing `app.py` calls `load_dotenv()` which reads `.env` — that file is gitignored and absent on Cloud. The app already has a graceful fallback (placeholder narrative when API key is absent), but to get real Claude output on Cloud the secret must be configured in Cloud settings. Format: `ANTHROPIC_API_KEY = "sk-ant-..."` pasted as TOML in Advanced Settings during deploy.
- **Demo file and template are the same file.** `demo/apple_financials.xlsx` is already the correct format. Serve it as both the demo input and the downloadable template — no need to build a separate blank template for v1.1.
- **Instructions and template must ship together.** Providing download without instructions, or instructions without download, each halves the value.

---

## MVP Definition

### Launch With (v1.1)

Minimum set to turn the existing bare uploader into a portfolio-ready live demo.

- [ ] Hero landing section — sets context; without it the first thing visitors see is a raw file uploader
- [ ] One-click Apple demo button — proof of output is the entire value proposition
- [ ] Demo download button — completes the demo loop
- [ ] In-app format instructions (accordion) — enables the upload-your-own path
- [ ] Downloadable Excel template — paired with instructions; removes format friction
- [ ] Tech stack / skills section — satisfies recruiter keyword scan with zero extra work
- [ ] `requirements.txt` verified for Cloud — deployment infrastructure blocker
- [ ] Streamlit Cloud deployment with API key secret — the milestone is moot without a live URL

### Add After Core is Stable (v1.1 polish)

- [ ] Generation stats (elapsed time + slide count) — add once the happy path is confirmed working on Cloud
- [ ] Visual polish pass (`st.columns`, spacing, section headers) — add once structure is locked; premature styling wastes time if layout changes

### Future Consideration (v2+)

- [ ] Multi-company comparison — architecture change to pipeline required
- [ ] PDF export — separate deliverable format, separate scope
- [ ] Real-time SEC / Yahoo Finance data ingestion — removes Excel dependency entirely

---

## Feature Prioritization Matrix

| Feature | Visitor Value | Implementation Cost | Priority |
|---------|--------------|---------------------|----------|
| Deployed URL (Cloud) | HIGH — everything else is moot without it | MEDIUM | P1 |
| One-click Apple demo | HIGH — proof of output | LOW | P1 |
| Hero / landing section | HIGH — first impression | LOW | P1 |
| Demo download button | HIGH — completes the loop | LOW | P1 |
| `requirements.txt` for Cloud | HIGH — blocker | LOW | P1 |
| In-app format instructions | MEDIUM — enables custom uploads | LOW | P1 |
| Downloadable Excel template | MEDIUM — removes friction | LOW | P1 |
| Tech stack / skills section | MEDIUM — recruiter signal | LOW | P1 |
| Generation stats | LOW-MEDIUM — credibility detail | LOW | P2 |
| Visual polish pass | MEDIUM — overall impression | LOW-MEDIUM | P2 |

**Priority key:**
- P1: Must ship for v1.1
- P2: Ship when P1 is stable
- P3: Future milestone

---

## Streamlit Cloud Deployment — Key Facts

Confidence: HIGH (verified from official Streamlit docs)

| Concern | Detail |
|---------|--------|
| Repo requirement | App must be in a **public** GitHub repo linked to your Streamlit account |
| Dependencies | `requirements.txt` in repo root; cannot mix package managers |
| Secrets | Paste TOML in Advanced Settings on deploy: `ANTHROPIC_API_KEY = "sk-ant-..."` |
| Secret access in code | Available as `os.environ["ANTHROPIC_API_KEY"]` or `st.secrets["ANTHROPIC_API_KEY"]` |
| Sleep behavior | Apps sleep after ~12h of no traffic; cold-start wake takes ~20-30s |
| Sleep workaround | None reliable on free tier; design UI to tolerate it (brief loading state is acceptable) |
| `load_dotenv()` on Cloud | No-op — `.env` not committed; existing graceful fallback activates (placeholder narrative) |
| Rate limits | No more than 5 app updates from GitHub per minute |

---

## Competitor / Reference Pattern Analysis

| Aspect | Typical bare Streamlit demo | Polished portfolio demo | Autopitch v1.1 approach |
|--------|----------------------------|------------------------|------------------------|
| First element | Raw `st.file_uploader` | Hero with tagline + CTAs | Hero with "Run Demo" and "Upload Your Own" buttons |
| Demo mode | Not standard | One-click sample data | One-click Apple data, immediate PPTX output |
| Skills visibility | None | README only | Inline expander or sidebar in the app itself |
| Template / format guidance | None | External docs link | In-app accordion + downloadable `.xlsx` |
| Deployment | Local instructions in README | Live URL, secrets handled | Streamlit Community Cloud + TOML secrets |
| Error handling | Raw traceback | Friendly message | Existing `ValidationError` string + "check template" pointer |

---

## Sources

- [Streamlit Community Cloud Secrets Management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management) — HIGH confidence, official docs
- [Streamlit Community Cloud Status and Limitations](https://docs.streamlit.io/deploy/streamlit-community-cloud/status) — HIGH confidence, official docs
- [st.secrets API Reference](https://docs.streamlit.io/develop/api-reference/connections/st.secrets) — HIGH confidence, official docs
- [Streamlit Community Discussion: Sleep / wake behavior](https://discuss.streamlit.io/t/web-apps-keeps-on-sleeping-after-30-minutes-or-a-day-of-inactivity/97350) — MEDIUM confidence, community corroboration
- [Portfolio UX patterns (WeAreDevelopers March 2025)](https://www.wearedevelopers.com/en/magazine/561/web-developer-portfolio-inspiration-and-examples-march-2025-561) — MEDIUM confidence, industry convention
- [Streamlit download button patterns](https://discuss.streamlit.io/t/download-button-with-excel-file/20794) — MEDIUM confidence, community practice
- [Building a Portfolio with Streamlit (Medium)](https://medium.com/data-science-in-your-pocket/building-portfolio-using-streamlit-ac215b8e74da) — LOW confidence, single source

---

*Feature research for: Autopitch v1.1 Portfolio Demo Polish*
*Researched: 2026-03-10*

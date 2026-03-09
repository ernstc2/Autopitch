# Feature Landscape

**Domain:** Consulting financial PowerPoint automation (Python, Big 4 style)
**Researched:** 2026-03-09
**Confidence note:** Web search and WebFetch tools were unavailable. All findings are based on training data (knowledge cutoff August 2025) covering Big 4 consulting conventions, python-pptx capabilities, financial analysis standards, and similar open-source tools (e.g., xlwings reports, openpyxl dashboards, reportlab decks). Confidence levels reflect this limitation.

---

## Table Stakes

Features users (and portfolio reviewers) expect. Missing any of these and the tool looks incomplete or like a student project.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Title slide with company name, period, date | Every deck starts here; missing = immediately unprofessional | Low | Company name parsed from Excel or CLI arg |
| Executive summary / key takeaways slide | Standard "so what" slide; consultants always lead with the punchline | Medium | 3-5 AI-generated bullets summarizing the full analysis |
| Revenue trend chart (bar or line, multi-year) | Core financial narrative; every analyst-day deck has this | Medium | Bar chart preferred for YoY comparison; needs 3+ years |
| Gross margin trend (line chart, % overlay) | Required to show operational efficiency story | Medium | Line overlay on revenue bar is the Big 4 convention |
| EBITDA and net margin summary | P&L analysis is incomplete without these two margin lines | Medium | Can share a slide with gross margin trend |
| Balance sheet snapshot slide | Assets / liabilities / equity summary; demonstrates financial statement coverage | Medium | Table-style or stacked bar showing composition |
| Cash flow summary slide | FCF and operating cash flow are key consulting metrics; missing = not a real 3-statement tool | Medium | Waterfall chart is the most impactful format here |
| Key metrics KPI bar (revenue growth %, margins, ratios) | Consulting decks always have a "scorecard" section | Medium | Computed: growth %, gross/EBITDA/net margins, current ratio, D/E, ROE, ROA |
| Consistent color theme across all slides | Visual inconsistency is the first thing reviewers notice | Low | One palette (navy/teal/grey) applied globally |
| Section divider slides | Big 4 decks use section breaks to signal structure; without them the deck feels like slides not a narrative | Low | Simple branded full-bleed color slides with section label |
| Slide numbers and footer (company name, date, confidential label) | Standard consulting deck footer; missing = looks like a draft | Low | Applied globally via slide master or per-slide |
| CLI interface `python generate.py input.xlsx` | Technical reviewers expect a clean entry point | Low | Must accept file path, optional output path |
| Streamlit web UI for file upload and download | Non-technical demo layer; shows engineering range | Medium | Upload Excel, click Generate, download PPTX |
| Demo Excel file with real company data | Reviewers need to run it themselves; synthetic data looks like you're hiding something | Low | Apple or Microsoft annual report data, 3-5 years |
| Input validation with clear error messages | Broken tools without good errors look unfinished | Medium | Missing sheets, wrong column names, non-numeric cells |
| README with setup, usage, and design decisions | Portfolio reviewers read the README first | Low | Must include: install, usage, template format, architecture decisions |

---

## Differentiators

Features that make this stand out as a portfolio piece. Not expected by default, but high signal for Big 4 tech consulting interviews.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| AI-generated insight-first slide titles | Titles like "Revenue grew 18% — Services mix shift the primary driver" vs "Revenue Trend" demonstrate AI integration and financial judgment | Medium | One Claude API call per deck; structured financial context as input prompt; use sonnet model |
| AI narrative bullets per section (2-3 per slide) | Mimics the analyst commentary Big 4 decks actually contain; shows LLM prompt engineering skill | Medium | Include growth drivers, anomalies flagged, comparisons to prior year |
| Waterfall chart for cash flow | Waterfall is the signature consulting chart type; most Python tools skip it because it's harder to build | High | Must build from scratch in matplotlib — no native waterfall in matplotlib/plotly without custom code |
| Anomaly / flag detection in narrative | "Gross margin compressed 4pp YoY — investigate COGS" adds analytical value beyond charting | Medium | Rule-based thresholds fed into AI prompt as context flags |
| Computed metrics beyond the basics | Working capital, cash conversion cycle, D/E, ROA, ROE signals deeper financial modeling knowledge | Medium | All computable from the three input statements |
| Structured Excel input template with documented schema | Demonstrates systems thinking — real consulting tools have input contracts | Low | Excel template file with headers pre-defined; included in repo |
| "Consulting voice" prompt engineering | Demonstrating that the AI output sounds like a Big 4 analyst write-up (not a blog post) is a skill signal | Medium | Prompt includes persona, output format constraints, financial context, tone guidance |
| Dual interface (CLI + Streamlit) from shared core | Shows clean separation of concerns; same output from two entry points | Medium | Core generate() function called identically from both; demonstrates good Python design |
| Branded slide master / template file | A custom .pptx template file (not just in-code styling) shows knowledge of the PowerPoint object model | Medium | Embed a pre-built template .pptx; python-pptx can apply layouts from a template |

---

## Anti-Features

Features to deliberately NOT build. These are scope creep risks that add complexity without proportional portfolio signal.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Multi-company comparison decks | 2x the input complexity, 2x the layout logic, marginal extra signal | One company, one deck, done well |
| Real-time data fetching (SEC EDGAR, Yahoo Finance, Alpha Vantage) | Auth complexity, API rate limits, data normalization effort; distracts from the actual demo | Static Excel input; note in README that data fetching could be Phase 2 |
| Custom branding / white-labeling (multiple themes) | One polished Big 4 theme demonstrates taste; multiple themes signals lack of focus | One great theme beats three mediocre ones |
| PDF export | PPTX is the consulting standard; PDF export is an ops task, not a financial insight task | Mention PDF is out of scope; presenters can export from PowerPoint directly |
| User authentication and accounts | Stateless local tool; auth adds infrastructure with zero portfolio signal for this type of project | No auth, no database, no user state |
| Interactive dashboard (Plotly Dash, Tableau-style) | A PowerPoint generator is the specific portfolio artifact — pivoting to dashboards is a different product | Streamlit is the right demo layer; don't scope-creep into analytics dashboards |
| Financial forecasting / projections | Forward-looking models require assumptions that are hard to validate; adds domain complexity without clean payoff | Historical analysis only; note forecasting could be an extension |
| Slide editing / annotation UI | Building a slide editor is a different product (Google Slides clone); not the value prop | Generate-and-done is the right UX contract |
| Natural language query interface ("tell me about margins") | Conversational AI UX is a different product category; adds complexity, confuses the demo story | Structured deck output is the demo story; keep it focused |
| Batch processing (multiple companies) | Multiplies input/output complexity; single-company is the right v1 scope | Note batch as future work in README |

---

## Feature Dependencies

```
Excel input validation
  → Metric computation (requires clean, parsed data)
    → Chart generation (requires computed metrics)
      → Slide assembly (requires charts as images)
        → AI narrative generation (requires computed metrics + slide context)
          → Final PPTX output

Slide master / template file
  → All slides (layout, fonts, colors inherit from master)

CLI interface
  → Core generate() function (calls validation → metrics → charts → AI → slides)

Streamlit UI
  → Core generate() function (same pipeline, different entry point)

Demo Excel file
  → README demo instructions
  → Automated test fixture (if tests are added)
```

---

## Slide Deck Structure (12-15 slides)

The following is the recommended slide sequence based on standard Big 4 financial deck conventions. This is what portfolio reviewers will expect to see.

| # | Slide Type | Content | Chart Type | Notes |
|---|-----------|---------|-----------|-------|
| 1 | Title | Company name, period covered, generated date | None | AI: no narrative needed |
| 2 | Executive Summary | 4-5 AI insight bullets, top metrics scorecard | KPI tiles | Highest-signal slide |
| 3 | Section divider | "Financial Performance" label | None | Navy full-bleed |
| 4 | Revenue Overview | Revenue by year, growth % annotations | Clustered bar + line overlay | 3-5 years |
| 5 | Profitability | Gross / EBITDA / Net margins trend | Multi-line chart | % values, not absolute |
| 6 | P&L Waterfall (optional) | Bridge from revenue to net income | Waterfall | High complexity but high signal |
| 7 | Section divider | "Balance Sheet" label | None | |
| 8 | Balance Sheet Snapshot | Assets / Liabilities / Equity composition | Stacked bar | Current + 1 prior year |
| 9 | Liquidity & Leverage | Current ratio, D/E ratio, working capital | KPI tiles + bar | Computed metrics |
| 10 | Section divider | "Cash Flow" label | None | |
| 11 | Cash Flow Summary | Operating / Investing / Financing by year | Grouped bar | |
| 12 | FCF Bridge | FCF from operating cash flow minus capex | Waterfall or simple bar | |
| 13 | Section divider | "Key Metrics" label | None | |
| 14 | Financial Scorecard | All computed ratios in one view | Table or KPI tiles | ROE, ROA, margins, ratios |
| 15 | Appendix / Data Notes | Input data source, methodology notes | None | Adds credibility |

---

## MVP Recommendation

For a portfolio project targeting Big 4 tech consulting interviews, prioritize in this order:

1. Three-statement Excel parsing with validation — the foundation; nothing else works without it
2. Metric computation (all 9+ metrics) — demonstrates financial domain knowledge explicitly
3. Chart generation (bar, line, waterfall) — the visual output is what reviewers screenshot for their notes
4. AI narrative (insight-first titles + 2-3 bullets) — the differentiating feature; must be present
5. PPTX assembly with consistent Big 4 styling — quality of output is what gets shared in interviews
6. CLI interface — required for technical reviewers to run it themselves
7. Streamlit UI — required for non-technical demo; secondary to the core pipeline
8. Demo Excel file (Apple or Microsoft) — required to make the README demo runnable

Defer:
- **P&L waterfall bridge** (slide 6): High complexity; include only if core pipeline is solid and time permits. A grouped bar works as a fallback.
- **Anomaly detection rules**: Nice-to-have for AI prompt context; add after narrative baseline is working.
- **Custom .pptx template master**: Start with in-code styling; migrate to a template file if time allows — it's a quality-of-life upgrade, not a functional requirement.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Big 4 deck conventions (slide types, style) | HIGH | Well-documented in training data; McKinsey/Deloitte deck structures are extensively published |
| Financial metrics (what to compute) | HIGH | Standard finance curriculum; P&L/BS/CF analysis is stable domain knowledge |
| Python library capabilities (python-pptx, matplotlib) | MEDIUM | Training data current to Aug 2025; verify waterfall chart approach against python-pptx 1.x docs |
| AI narrative prompt engineering | MEDIUM | Claude API conventions known; verify current claude-sonnet model ID and token limits |
| Portfolio signal for Big 4 interviews | MEDIUM | Based on published job descriptions and interview prep content; not verified against current 2026 JDs |
| Competitor tool landscape | LOW | Could not search; tools like Beautiful.ai, Gamma.app, Tome exist but feature comparison not verified |

---

## Sources

- Training data: Big 4 consulting deck conventions (Deloitte, McKinsey, PwC publicly available frameworks)
- Training data: python-pptx library documentation (v0.6.x, last verified August 2025)
- Training data: Financial analysis curriculum (CFA, MBA finance courses) for metric definitions
- Training data: Consulting interview prep content for portfolio project evaluation criteria
- Note: Web search and WebFetch were unavailable; competitor tool landscape (Beautiful.ai, Gamma, Tome, etc.) was not verified against current 2026 feature sets. LOW confidence on competitive positioning.

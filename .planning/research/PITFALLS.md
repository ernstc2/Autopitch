# Domain Pitfalls

**Domain:** Python Excel-to-PowerPoint financial deck generator with AI narrative
**Project:** Autopitch
**Researched:** 2026-03-09 (v1.0 core pipeline) | updated 2026-03-10 (v1.1 portfolio demo features)
**Confidence note:** v1.0 section based on training-data knowledge. v1.1 section verified against Streamlit official docs and Anthropic API docs (see sources).

---

## Critical Pitfalls

Mistakes that cause rewrites, broken output, or demo failures.

---

### Pitfall 1: Formula Cells Return None Instead of Values

**What goes wrong:** openpyxl reads `.xlsx` files in data-only mode by default when formulas are present. If the file was never opened and saved in Excel after the formulas were written (i.e., the cached value was never written back), `cell.value` returns `None`. Financial models built entirely in Excel are often formula-heavy — revenue, margins, subtotals — all return `None`.

**Why it happens:** `.xlsx` format stores formula results as cached values alongside the formula. If the file is programmatically generated or the cache is stale, openpyxl sees no cached value.

**Consequences:** Silent `None` data flows into metric calculations, producing `NaN` pandas values or `TypeError` crashes. Charts render as flat/empty. LLM receives "None" values in its prompt and generates nonsense narrative.

**Prevention:**
- Always open with `openpyxl.load_workbook(path, data_only=True)` — this reads cached values instead of formulas.
- After parsing, run a validation pass: count `None` values per expected column and raise a user-facing error if any required financial line items are null.
- In the documented Excel template, require that the file be saved in Excel at least once (so caches are populated). State this explicitly in the README.

**Detection:** Add a `validate_parsed_data()` function in Phase 1 that checks all required row labels exist and all value columns are non-null. Fail loudly with a row-level error message rather than silently propagating `None`.

**Phase:** Excel parsing (Phase 1 / core data layer). Must be solved before any downstream work.

---

### Pitfall 2: python-pptx Slide Layouts Are Positional, Not Named

**What goes wrong:** `prs.slide_layouts[1]` gives you whatever layout happens to be at index 1 in the template file's layout list. If you hardcode layout indices and then swap the `.pptx` template file (e.g., to a different Big 4 theme), all slides silently use wrong layouts. Layouts also have different placeholder indices per template — `slide.placeholders[1]` for "body text" in one template may be "subtitle" in another.

**Why it happens:** python-pptx provides no stable name-based API for layout lookup. Placeholder indices are template-defined, not standardized.

**Consequences:** Slide content lands in wrong positions, titles appear in body areas, or `KeyError` crashes when a placeholder index doesn't exist in the new template.

**Prevention:**
- Access layouts by name: `next(l for l in prs.slide_layouts if l.name == "Title and Content")`. Use exact layout names from the template.
- Document all layout names and placeholder indices used, in a `SLIDE_TEMPLATE.md` file.
- Access placeholders by `ph.placeholder_format.idx` (the integer idx), not by list position, and define a constant map: `TITLE_IDX = 0`, `BODY_IDX = 1`.
- Commit the `.pptx` template file to the repo — never swap it without updating constants.

**Detection:** Write a `verify_template()` function that runs at startup and asserts all required layout names and placeholder indices exist. Fail immediately if the template doesn't match expectations.

**Phase:** PowerPoint generation setup (Phase 2). Establish the constant map and verification before building any slides.

---

### Pitfall 3: Matplotlib Charts Embedded as Images Lose Resolution or Scale Incorrectly

**What goes wrong:** Charts saved as PNG and inserted into slides via `add_picture()` appear blurry at presentation zoom levels, or are mis-sized relative to the slide area. python-pptx positions images by top-left corner + explicit width/height in EMUs (English Metric Units). Pixel dimensions do not map to EMU correctly unless DPI is controlled.

**Why it happens:** Default matplotlib DPI (100) produces raster images that look fine on screen but blur when projected. EMU conversion is non-obvious: 1 inch = 914400 EMUs. If width/height are guessed or hardcoded in pixels, sizing is wrong.

**Consequences:** Blurry charts in the demo deck — the most visible artifact to an interviewer reviewing the output. Charts that overflow slide boundaries or appear too small.

**Prevention:**
- Save all charts at 150–200 DPI: `fig.savefig(buf, dpi=150, bbox_inches='tight', facecolor='white')`.
- Use `io.BytesIO` as the save target (no temp files needed), then pass the buffer directly to `add_picture()`.
- Define slide dimensions from `prs.slide_width` and `prs.slide_height` in EMUs and compute chart positions as proportions: `left = Inches(0.5)`, `width = prs.slide_width - Inches(1.0)`.
- Use `Inches()` and `Pt()` helper functions from `pptx.util` rather than raw EMU integers.

**Detection:** Run the deck generator against the demo data file and visually inspect the output in PowerPoint/LibreOffice before any release.

**Phase:** Chart generation (Phase 2/3). Establish the DPI and sizing constants in the first chart implementation and reuse throughout.

---

### Pitfall 4: LLM Prompt Produces Generic Text Instead of Insight-First Consulting Language

**What goes wrong:** Prompts like "summarize these financials" produce safe, flat prose: "Revenue was $X. Gross margin was Y%." This does not match consulting deck conventions where titles are insight-first ("Revenue Growth Accelerated to 15% Despite Macro Headwinds") and bullets lead with the "so what" not the data.

**Why it happens:** The model defaults to descriptive reporting unless explicitly instructed to produce insight-first language. Financial prompts without structure produce unstructured responses.

**Consequences:** The AI-generated narrative undermines the portfolio impression — it makes the tool look like a simple data dump with an API call bolted on, rather than a genuine analysis tool.

**Prevention:**
- System prompt must explicitly specify the persona and output contract: "You are a senior consultant at a Big 4 firm writing slide commentary. Every slide title must be an insight statement, not a label. Every bullet must lead with the business implication, not the metric."
- Provide a one-shot example in the prompt: show one complete slide title + 2 bullets in the exact format required.
- Structure the financial context passed to the model as labeled key-value pairs (not prose), so the model can reference specific numbers: `Revenue Growth YoY: +14.2%`, `Gross Margin: 43.1% (vs 41.8% prior year)`.
- Request structured JSON output from the model (title + bullets per slide) rather than freeform prose — this prevents the model from adding unwanted preamble and makes parsing deterministic.

**Detection:** Run a prompt test against the demo data file and manually review all 12-15 slide outputs before shipping. Specifically check: are all titles insight-first? Do bullets start with implication or data?

**Phase:** LLM integration (Phase 3). Nail the system prompt and output schema before wiring into the deck generator.

---

### Pitfall 5: Single LLM Call for the Entire Deck Hits Token Limits or Produces Inconsistent Quality

**What goes wrong:** Passing all financial metrics for all three statements in one prompt and requesting 12-15 slides of output in a single response frequently produces: truncated output (hitting output token limits), inconsistent quality across slides (early slides are stronger than later ones), or malformed JSON when the response is cut off.

**Why it happens:** claude-sonnet has a large context window but output length is bounded. Requesting 15 structured slides in one call pushes close to typical output token limits. The model also degrades in quality toward the end of very long generations.

**Consequences:** Partial deck narrative, JSON parse errors crashing the generator, or visibly weaker commentary on the final slides.

**Prevention:**
- The PROJECT.md says "one call per deck" — this is valid if scoped correctly. Design the output schema to be concise: each slide = 1 title string + list of 2-3 bullet strings (each bullet max 15 words). This keeps total output well within limits.
- Cap bullet length in the prompt: "Each bullet must be 12-15 words maximum."
- Wrap the API call in a response validator that checks the returned JSON has exactly the expected number of slide entries before using it.
- If output is truncated, the fallback should be to re-call for only the missing slides rather than crashing.

**Detection:** Count tokens in the constructed prompt before sending (use `anthropic` SDK token counting if available, or estimate at ~0.75 tokens/word). Log the full response length. Test with the real demo data file.

**Phase:** LLM integration (Phase 3).

---

### Pitfall 6: Streamlit File Upload Writes to Temp Path That Is Cleaned Up Mid-Processing

**What goes wrong:** `st.file_uploader()` returns a `UploadedFile` object, not a filesystem path. Code that passes a file path string (e.g., to `openpyxl.load_workbook(path)`) fails when given the Streamlit object. Additionally, if the uploaded file is written to a temp path and processing is slow, Streamlit may reset session state between reruns, making the temp file appear to disappear.

**Why it happens:** Streamlit's execution model re-runs the entire script on every widget interaction. The `UploadedFile` object is a BytesIO-like object, not a path. Developers familiar with CLI file handling don't expect this.

**Consequences:** `FileNotFoundError` or type errors when the CLI code is reused directly in the Streamlit UI. Intermittent failures that only appear after slow LLM calls complete.

**Prevention:**
- Design the core parsing layer to accept `Union[str, BinaryIO]` — both a path string and a file-like object. Use `openpyxl.load_workbook(filename_or_stream)` which accepts both.
- In the Streamlit UI layer, pass `uploaded_file` (the BytesIO-like object) directly — do not write to temp files.
- Wrap the entire deck generation call in `st.spinner()` and trigger it from a button click (not a reactive re-run) to prevent mid-processing reruns.
- Store the generated PPTX bytes in `st.session_state` so it persists across reruns for the download button.

**Detection:** Test the Streamlit flow end-to-end with a slow LLM call (add a `time.sleep(3)` stub) and verify the download button still works after the delay.

**Phase:** Streamlit UI (Phase 4). The CLI-to-Streamlit integration layer is where this manifests.

---

## Moderate Pitfalls

---

### Pitfall 7: Merged Cells in Excel Cause Row Parsing to Misalign

**What goes wrong:** Financial statements downloaded from investor relations pages or built by analysts often use merged cells for section headers (e.g., "Operating Expenses" spanning three columns). openpyxl returns `None` for all but the top-left cell in a merge. Row iteration that assumes every cell in column A is a line item label will silently skip or misread merged header rows.

**Prevention:**
- Use `ws.merged_cells` to detect and unmerge before row iteration, or explicitly skip rows where column A is `None` after identifying them as section headers.
- In the documented input template, prohibit merged cells — require that the P&L, Balance Sheet, and Cash Flow sheets use flat, unmerged row/column structures. State this in the README and in a `TEMPLATE_FORMAT.md`.

**Phase:** Excel parsing (Phase 1).

---

### Pitfall 8: Financial Metrics Computed from Wrong Sign Conventions

**What goes wrong:** Excel financial models vary in sign convention: some models represent expenses as positive numbers (implied subtraction), others as negative. EBITDA margin computed as `(EBITDA / Revenue) * 100` gives a negative result if expenses are stored as negatives that weren't sign-flipped.

**Prevention:**
- Document the required sign convention for every line item in the input template spec.
- Add assertion-based validation: revenue must be positive, COGS must be positive (subtract in formulas), net income can be negative. Fail clearly if a value violates the expected sign.
- Compute EBITDA as `Operating Income + D&A` rather than from raw expense lines where possible — reduces sign dependency.

**Phase:** Metric computation (Phase 1/2).

---

### Pitfall 9: Waterfall Chart Is Not Natively Supported in python-pptx

**What goes wrong:** The PROJECT.md requires waterfall charts. python-pptx's chart API is limited to a subset of chart types: bar, line, pie, scatter, area. Waterfall is not in this set. Attempts to add a waterfall chart via the native API will fail or require undocumented XML manipulation.

**Prevention:**
- Build waterfall charts using matplotlib (stacked bar technique with invisible base bars) and embed as images — this is the standard workaround and produces identical visual output.
- Do not attempt to use the python-pptx native chart XML for waterfall. The matplotlib route is more controllable and styled more easily.
- Apply the Big 4 color scheme (navy/teal) in matplotlib's `rcParams` once at module level so all charts inherit the theme.

**Phase:** Chart generation (Phase 2/3). Establish this early to avoid a late-stage refactor when waterfall charts are first attempted.

**Confidence:** HIGH — python-pptx chart type list is well-documented. Waterfall is confirmed absent.

---

### Pitfall 10: python-pptx Native Charts Cannot Be Styled to Arbitrary Brand Standards

**What goes wrong:** python-pptx's chart API exposes styling via XML manipulation (`chart.chart_format`, series fills, axis formatting). It is verbose, fragile, and poorly documented. Achieving exact Big 4 color consistency across all chart types (correct hex values, no default Office blues) requires setting properties at multiple nested levels.

**Prevention:**
- Use matplotlib for ALL charts and embed as images. This gives full styling control via `rcParams`, avoids python-pptx chart XML entirely, and produces consistent output across chart types.
- Define a single `CHART_STYLE` dict with brand colors, font sizes, grid settings, and apply it to every `fig, ax` before plotting.
- Avoid mixing python-pptx native charts and matplotlib images in the same deck — pick one approach and be consistent.

**Phase:** Chart generation (Phase 2/3). Commit to matplotlib-as-images from day one.

---

### Pitfall 11: LLM JSON Response Parsing Breaks on Markdown Code Fences

**What goes wrong:** Claude (and other models) often wrap JSON responses in markdown code fences (` ```json ... ``` `) even when instructed to return raw JSON. `json.loads()` called directly on this response raises `JSONDecodeError`.

**Prevention:**
- Strip code fences before parsing: `response = re.sub(r'^```json\s*|\s*```$', '', response.strip())`.
- Alternatively, use the anthropic SDK's tool-use / structured output feature to get guaranteed-clean JSON.
- Log the raw response before parsing so failures are debuggable.

**Phase:** LLM integration (Phase 3).

---

### Pitfall 12: Hardcoded Row Labels Fail on Real-World Financial Statement Variations

**What goes wrong:** The parser looks for `"Revenue"` in column A to locate the revenue row, but the uploaded Excel says `"Total Net Revenue"` or `"Net Sales"`. Label matching by exact string is brittle across companies.

**Prevention:**
- Use case-insensitive fuzzy matching (e.g., `rapidfuzz` or a simple contains-check) for row label identification.
- Define a `LABEL_ALIASES` dict: `{"revenue": ["revenue", "total revenue", "net revenue", "net sales", "total net revenue"]}`.
- If no match found for a required line item, raise a clear error: "Could not find 'Revenue' row. Expected one of: [aliases]. Check your P&L sheet structure."
- For the demo data and documented template, use canonical label names and validate against them strictly — this keeps the happy path clean while the alias system handles edge cases.

**Phase:** Excel parsing (Phase 1).

---

## Minor Pitfalls

---

### Pitfall 13: BytesIO Buffer Position Not Reset Before Reading

**What goes wrong:** After writing a PPTX to a `BytesIO` buffer with `prs.save(buf)`, the buffer's position is at the end. Reading it immediately for a Streamlit download gives an empty file.

**Prevention:** Always call `buf.seek(0)` after `prs.save(buf)` and before passing `buf.getvalue()` or the buffer to `st.download_button()`.

**Phase:** Streamlit UI (Phase 4). One-line fix, but causes an invisible silent failure if missed.

---

### Pitfall 14: Fonts Not Embedded in PPTX Cause Layout Shift on Recipient's Machine

**What goes wrong:** python-pptx slides use fonts by name. If the recipient's machine doesn't have the font (e.g., custom Big 4 fonts), PowerPoint substitutes a fallback font with different metrics, causing text overflow and layout breakage.

**Prevention:**
- Use universally available fonts: Calibri (Office default), Arial, or open-source alternatives.
- Avoid any custom font that isn't installed by default on Windows/Mac Office.
- Test the output `.pptx` on a clean machine (or a VM without custom fonts).

**Phase:** PowerPoint generation setup (Phase 2).

---

### Pitfall 15: Streamlit Reruns Trigger Multiple LLM API Calls

**What goes wrong:** Without state guards, Streamlit's reactive re-run model may trigger the API call multiple times (e.g., when the user adjusts a widget after generation). This wastes API credits and slows the UI.

**Prevention:**
- Gate the LLM call behind a button click, not a reactive widget dependency.
- Store the generated deck bytes in `st.session_state["deck_bytes"]` after first generation and check for it before re-calling.

**Phase:** Streamlit UI (Phase 4).

---

### Pitfall 16: Slide Count Mismatch Between LLM Output and Slide Templates

**What goes wrong:** If the LLM returns 11 slide entries but the deck generator expects 13, the unmatched slides either get empty placeholders or raise `IndexError` when iterating.

**Prevention:**
- Design the deck generator to drive slide creation from the LLM's returned structure (iterate over returned slides), not from a hardcoded slide count.
- Validate that the LLM returned at least the minimum required slides; pad with a "Data Unavailable" placeholder if below minimum.

**Phase:** Integration of LLM output with deck generator (Phase 3/4).

---

---

# v1.1 Portfolio Demo Feature Pitfalls

*Added: 2026-03-10. Focus: adding portfolio demo UI, skills showcase, data templates, and Streamlit Cloud deployment to the existing app.*
*Confidence: HIGH — verified against Streamlit official docs and Anthropic API docs.*

---

## Critical Pitfalls (v1.1)

---

### Pitfall 17: API Key Committed to Public Repository

**What goes wrong:**
The `.env` file contains `ANTHROPIC_API_KEY`. When the repo is made public for Streamlit Cloud deployment, or a `secrets.toml` file is accidentally committed, the key is exposed. GitHub's secret scanning notifies Anthropic, who auto-revokes the key. The live demo breaks immediately — often before the first visitor arrives.

**Why it happens:**
Developer makes the repo public for Streamlit Cloud and forgets the key exists in `.env`. Or creates `.streamlit/secrets.toml` for local testing and commits it alongside other config files, not realizing it contains the key.

**How to avoid:**
- Confirm `.gitignore` covers both `.env` and `.streamlit/secrets.toml` before setting repo visibility to public
- Add `.streamlit/secrets.toml` to `.gitignore` now, before creating it, even if just for local use
- Set `ANTHROPIC_API_KEY` only through the Streamlit Community Cloud dashboard (Advanced Settings → Secrets) — never in any file that touches version control
- In `app.py`, access the key via `st.secrets["ANTHROPIC_API_KEY"]` with a fallback to `os.getenv("ANTHROPIC_API_KEY")` for local dev compatibility

**Warning signs:**
- Repo is "Public" on GitHub but the Streamlit Cloud secrets panel has not been configured
- `git status` shows `.env` or `secrets.toml` as a new untracked file right before going public
- App works locally (dotenv path) but fails on Cloud with `AuthenticationError`

**Phase to address:**
Streamlit Cloud Deployment phase — first task before any other deployment work.

---

### Pitfall 18: Download Button Triggers Full App Rerun, Losing the Generated Deck

**What goes wrong:**
The current `app.py` generates `pptx_bytes` inside the `if st.button("Generate Deck"):` block and immediately renders `st.download_button`. When the user clicks "Download PPTX", Streamlit reruns the entire script. The generate block does not re-execute (button state is not sticky), so `pptx_bytes` goes out of scope and the download button disappears. The user must regenerate.

**Why it happens:**
`st.download_button` is a widget; clicking it triggers a script rerun like any other widget. Variables set inside `if st.button():` blocks are not automatically persisted between reruns.

**How to avoid:**
- Store `pptx_bytes` in `st.session_state["pptx_bytes"]` immediately after generation
- Render `st.download_button` unconditionally from session state on every rerun, not nested inside the generate block
- Optionally use `on_click="ignore"` on the download button (suppresses the rerun entirely for a pure frontend download action)

**Warning signs:**
- Clicking "Download PPTX" clears the success message and the button itself
- User must click "Generate Deck" again after every download attempt
- This is not apparent in local dev because the generate button is clicked frequently during testing

**Phase to address:**
Demo-first Landing / Core UI Polish phase — fix session state persistence before building any demo flow on top.

---

### Pitfall 19: Streamlit Cloud App Sleeps After 12 Hours — Demo Invisible to Portfolio Visitors

**What goes wrong:**
Streamlit Community Cloud hibernates apps with no traffic after approximately 12 hours. A recruiter visiting the portfolio link sees a "This app has gone to sleep" page with a manual wake button. Many visitors click away rather than waiting the 30-second wake time. The demo investment is wasted at the highest-stakes moment.

**Why it happens:**
Free tier resource conservation policy. No built-in option exists to prevent this on the free plan.

**How to avoid:**
- Set up a GitHub Actions cron job that sends a GET request to the app URL every 6 hours — this counts as traffic and keeps the app awake
- Add a one-line note to the portfolio page: "Live demo — may take ~30s to wake if inactive." Setting expectations reduces abandonment
- Commit the keep-alive workflow before sharing the live URL publicly

**Warning signs:**
- No keep-alive mechanism in place before the portfolio link is shared
- App URL has received no visits in 12+ hours

**Phase to address:**
Streamlit Cloud Deployment phase — configure keep-alive workflow immediately after first successful deployment.

---

### Pitfall 20: Dev Dependencies in requirements.txt Bloat Build and Risk Conflicts

**What goes wrong:**
The current `requirements.txt` includes `pytest>=8.0.0` and `pytest-cov>=5.0.0`. These are dev-only dependencies. On Streamlit Cloud they increase build time and can create dependency conflicts (pytest pulls in `pluggy`, `iniconfig`, `packaging` which may conflict with pinned versions of production packages). Streamlit Cloud reads only `requirements.txt` — there is no separation.

**Why it happens:**
Single-file dev+prod requirements is the fastest path early in a project and works fine locally. The problem surfaces at deployment time.

**How to avoid:**
- Create `requirements-dev.txt` containing `-r requirements.txt` plus `pytest`, `pytest-cov`, and any other dev tools
- Strip `requirements.txt` down to production-only deps: `anthropic`, `openpyxl`, `pydantic`, `streamlit`, `python-dotenv`, `python-pptx`, `matplotlib`
- Streamlit Cloud only reads `requirements.txt` — dev deps stay out of the build entirely

**Warning signs:**
- `requirements.txt` contains `pytest`, `pytest-cov`, `black`, `mypy`, or similar
- Streamlit Cloud build log shows conflict warnings during dependency resolution
- Build time is disproportionately long

**Phase to address:**
Streamlit Cloud Deployment phase — clean up requirements.txt before the first deployment attempt.

---

### Pitfall 21: python-pptx and matplotlib Missing from requirements.txt — Silent Build Failure

**What goes wrong:**
The current `requirements.txt` does not include `python-pptx` or `matplotlib`. They are installed locally in the virtual environment but not declared. On Streamlit Cloud, they are absent. The app fails with `ModuleNotFoundError` at runtime, not at build time. Chart generation and deck building are completely broken on Cloud even though they work locally.

**Why it happens:**
Packages installed locally during development without being added to `requirements.txt` — an extremely common omission. There is no build-time enforcement that all imports have corresponding requirements entries.

**How to avoid:**
- Add `python-pptx>=1.0.0` and `matplotlib>=3.8.0` to `requirements.txt` before first deployment
- After deployment, verify a complete deck is generated on Cloud by running the Apple demo end-to-end and opening the downloaded PPTX
- Run `pip list` in the virtual env and diff against `requirements.txt` to catch any other missing packages

**Warning signs:**
- `python-pptx` and `matplotlib` not in `requirements.txt` (confirmed — they are absent in the current file)
- Streamlit Cloud build log shows no mention of these packages being installed
- App errors immediately on deck generation with `ModuleNotFoundError`

**Phase to address:**
Streamlit Cloud Deployment phase — fix requirements.txt before the first deployment attempt. This is a guaranteed deployment failure if not addressed.

---

## Moderate Pitfalls (v1.1)

---

### Pitfall 22: One-Click Demo Calls Claude API on Every Button Press — API Costs and 429 Risk

**What goes wrong:**
The one-click Apple demo calls `run_pipeline()` on every click, which includes a full Anthropic API call. Rapid successive clicks (or a widely shared link) accumulate API costs and can hit rate limits, returning a 429 error as a raw traceback during a live recruiter demo.

**Why it happens:**
The pipeline is stateless by design — every call goes all the way through. No caching layer exists.

**How to avoid:**
- Wrap the Apple demo call in `@st.cache_data` keyed on the demo file's content hash — generates once per session, returns cached bytes on subsequent clicks
- Catch `anthropic.RateLimitError` and `anthropic.APIError` explicitly and show a user-friendly error message instead of a traceback
- Consider pre-generating the Apple deck as a static `.pptx` asset committed to the repo — eliminates API cost on demo entirely, though at the cost of showing a fixed rather than live-generated output (label it clearly if doing this)

**Warning signs:**
- No `@st.cache_data` on the demo generation path
- API errors surfaced as raw Python exceptions
- Multiple rapid test clicks during development noticeably drain API credits

**Phase to address:**
Demo-first Landing phase — caching strategy must be decided before wiring the one-click demo button.

---

### Pitfall 23: Skills Showcase Section Reads as Resume Padding, Not Technical Evidence

**What goes wrong:**
A tech badge wall listing "Python, Streamlit, Pydantic, Anthropic API..." without context provides no signal to a technical reviewer. Recruiters who know the stack see it as filler; those who don't know the stack can't evaluate it. The section actively hurts the impression by taking up space without adding value.

**Why it happens:**
Skill lists are the default pattern for portfolio tech showcases. Adding decision rationale requires knowing the codebase, which takes extra effort. The temptation is to ship the list and move on.

**How to avoid:**
- For each key technology, write one sentence explaining the specific decision that was made and why: "Pydantic v2 frozen models — enforces immutable data contracts through the pipeline, preventing silent state mutation between parse, compute, and render phases"
- Limit the list to 5-6 technologies that represent genuine architectural decisions. Omit boilerplate items (pytest, git, VS Code)
- Link each item to the relevant source file so reviewers can verify claims directly

**Warning signs:**
- Skills section is a list of library names with no rationale
- Items like "Git" or "pytest" are included (signals padding, not design thinking)
- The section is longer than the demo explanation

**Phase to address:**
Skills Showcase phase.

---

### Pitfall 24: File Uploader Shown Before Demo — Buries the Main Value Proposition

**What goes wrong:**
Showing the file uploader widget as the primary UI element forces every visitor to bring their own Excel file before they can see anything. Portfolio visitors (recruiters, interviewers) will not have a compatible Excel file ready. The tool's capability is gated behind a prerequisite that most visitors cannot fulfill. They leave without seeing anything.

**Why it happens:**
The current `app.py` was built for actual users who have data. Portfolio visitors are a different audience.

**How to avoid:**
- Hero section first: description of what the tool does + "Try the Apple demo" button prominently above the fold
- File uploader second: in a separate section labeled "Upload your own data" with a link to the template download
- Use tabs or visual hierarchy (not buried expanders) to make both paths equally discoverable

**Warning signs:**
- `st.file_uploader` is the first visible element on the page
- There is no way to generate a deck without uploading a file
- A visitor who lands on the page sees a file upload widget with no context

**Phase to address:**
Demo-first Landing phase.

---

### Pitfall 25: Excel Template Download Returns Corrupt or Empty File

**What goes wrong:**
A downloadable Excel template created with openpyxl and served via `st.download_button` can silently produce a corrupt file if: the BytesIO buffer position is not reset before calling `.getvalue()`, the MIME type is wrong (browser treats it as text), or the template file is opened from disk in text mode instead of binary mode.

**Why it happens:**
Binary file handling in Streamlit has several known footguns. The MIME type for xlsx is non-obvious. Community reports show the first few download clicks sometimes fail on deployed apps before subsequent clicks succeed — a transient Streamlit Cloud artifact.

**How to avoid:**
- Correct MIME type: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- If loading a pre-built template from disk: `open("demo/template.xlsx", "rb").read()` — binary mode explicitly
- If generating with openpyxl: `buf = BytesIO(); wb.save(buf); buf.seek(0); data = buf.getvalue()`
- Test the downloaded file opens without Excel repair prompts on both Windows and Mac

**Warning signs:**
- Excel opens the downloaded file with a "repair" prompt
- File size is 0 bytes or suspiciously small
- First download click shows "file not available" but later clicks work

**Phase to address:**
Data Template phase.

---

## Technical Debt Patterns (v1.1)

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Single `requirements.txt` for dev + prod | Less files to manage | Dependency conflicts, bloated Cloud build, confuses contributors | Never — split before first deployment |
| `load_dotenv()` only, no `st.secrets` fallback | Works locally | Fails on Streamlit Cloud where `.env` is absent | Never for deployed app — add `st.secrets` path |
| Skills list without decision rationale | Fast to write | Signals padding, not depth; reviewers skip it | Never for a portfolio targeting senior technical roles |
| Pre-generating Apple demo deck as static bytes | Eliminates API cost on demo | Demo does not reflect live Claude output | Acceptable if clearly labeled "pre-generated sample output" |
| Loose `>=` bounds on all packages in requirements.txt | Always installs latest | Output can change silently when matplotlib or python-pptx updates | Acceptable for non-rendering libs; pin matplotlib and python-pptx |

---

## Integration Gotchas (v1.1)

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Streamlit Cloud Secrets | Committing `secrets.toml` or using `load_dotenv()` only | Set key in Streamlit Cloud dashboard only; access via `st.secrets["ANTHROPIC_API_KEY"]` with `os.getenv` fallback |
| `st.download_button` + generated bytes | Nesting download button inside generate block without session state | Store bytes in `st.session_state`; render download button unconditionally from state |
| `st.download_button` + `.xlsx` template | Wrong MIME type or reading file in text mode | MIME: `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`; read in `"rb"` mode |
| Anthropic SDK on Cloud | `AuthenticationError` or `RateLimitError` shown as raw traceback | Catch both explicitly; show user-friendly messages; check `st.secrets` before `os.getenv` |
| Demo file path on Cloud | Hardcoded local path like `demo/apple_financials.xlsx` | Use `pathlib.Path(__file__).parent / "demo" / "apple_financials.xlsx"` for path-independent resolution |

---

## Performance Traps (v1.1)

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Claude API call on every demo button click | Slow app (10-15s per click), API costs accumulate, 429 risk | `@st.cache_data` on demo pipeline call keyed on file hash | Every click without caching |
| matplotlib figure leak | Memory grows with each deck generation; Cloud OOM after ~10 sessions | `plt.close('all')` after each figure saved to bytes | After ~10-20 deck generations in one session |
| No `max_upload_size` limit | Large user-uploaded files (>5 MB) slow parsing or timeout | Add `server.maxUploadSize = 10` in `.streamlit/config.toml` | Files significantly larger than Apple demo (~50 KB) |

---

## Security Mistakes (v1.1)

| Mistake | Risk | Prevention |
|---------|------|------------|
| `ANTHROPIC_API_KEY` in public repo or `secrets.toml` | Key auto-revoked within minutes; demo breaks; key must be regenerated | Gitignore `.env` and `.streamlit/secrets.toml`; set key only in Streamlit Cloud dashboard |
| Displaying `st.secrets` values in UI for debugging | Key visible to all app visitors | Never log or render secret values; remove all debug `st.write(st.secrets)` before deployment |
| No rate limiting on generate button | Rapid clicking drains API credits or triggers 429 | Disable generate button while pipeline is running using `st.session_state` flag |

---

## UX Pitfalls (v1.1)

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| File uploader shown before demo button | Recruiter cannot try tool without data; leaves without seeing output | Hero + demo button first; file uploader below the fold |
| No progress feedback during 10-15s API call | Visitor thinks app is frozen; abandons | `st.spinner` with descriptive message; optionally show stage labels |
| Download button disappears after click | User thinks download failed; regenerates unnecessarily | Persist download button in session state until new file is uploaded |
| Template instructions buried in expander | Users who want custom data give up finding the format | Inline instructions in upload section; template download link next to uploader |
| Skills showcase section has no decision rationale | Technical reviewers dismiss it as padding | 5-6 items max, each with one-sentence rationale linked to a source file |

---

## "Looks Done But Isn't" Checklist (v1.1)

- [ ] **Secrets on Cloud:** App runs without local `.env` file — test by temporarily removing `.env` and relying on `st.secrets` path
- [ ] **Download persistence:** Clicking "Download PPTX" 3 times without regenerating keeps the button and bytes visible each time
- [ ] **Demo file accessible on Cloud:** `demo/apple_financials.xlsx` is committed to the repo (not gitignored) and the path resolves correctly at Cloud runtime
- [ ] **Keep-alive active:** GitHub Actions keep-alive workflow is enabled and has run at least once before the portfolio link is shared
- [ ] **Dev deps removed:** `requirements.txt` does not include `pytest` or `pytest-cov` — verified in Streamlit Cloud build log
- [ ] **python-pptx and matplotlib listed:** Cloud build log shows these packages installed; deck generation works end-to-end on Cloud
- [ ] **Template download opens cleanly:** Downloaded `.xlsx` opens in Excel without a repair prompt; all sheets and formatting present
- [ ] **API errors are friendly:** Supplying an invalid API key shows a user-readable message, not a raw traceback
- [ ] **Demo button loads within 5 seconds:** Hero section and one-click demo are visible without scrolling on a 1280px viewport

---

## Recovery Strategies (v1.1)

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| API key committed to public repo | MEDIUM | Revoke key immediately in Anthropic console; generate new key; add to Streamlit Cloud secrets; audit git history with `git log --all -S 'ANTHROPIC'` |
| Cloud build fails (missing python-pptx/matplotlib) | LOW | Add missing packages to `requirements.txt`; push to GitHub; Streamlit Cloud auto-redeploys |
| Download button loses bytes on rerun | LOW | Add `st.session_state` storage for `pptx_bytes`; 30-minute fix |
| App sleeping when demo link is shared | LOW | Visit URL to wake; add GitHub Actions keep-alive for future; add sleep-note to portfolio page |
| API 429 error during live demo | LOW | Add `anthropic.RateLimitError` handler with friendly message; add `@st.cache_data` on demo call |
| Excel template download corrupted | LOW | Fix BytesIO `seek(0)` call and MIME type; redeploy |

---

## Pitfall-to-Phase Mapping

### v1.0 Core Pipeline

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Formula cells return None | Excel parsing phase | All required rows non-null for demo data |
| Merged cell misalignment | Excel parsing phase | Parser handles Apple financials without error |
| Sign convention errors | Metric computation phase | EBITDA margin positive for Apple data |
| Layout indices brittle | PowerPoint setup phase | `verify_template()` passes on all required layouts |
| Waterfall chart absent from python-pptx | Chart generation phase | Waterfall renders correctly in output deck |
| LLM returns generic text | LLM integration phase | All 12+ slide titles are insight-first |
| JSON wrapped in code fences | LLM integration phase | Parser handles fence-wrapped and bare JSON |
| BytesIO not reset | Streamlit UI phase | Downloaded PPTX is non-empty and valid |

### v1.1 Portfolio Demo Features

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| API key in public repo | Deployment phase (first task) | `git log --all --full-history -- .env` returns nothing; Cloud runs without local `.env` |
| Download button loses bytes on rerun | UI Polish / Demo Landing phase | Download button persists after 3 clicks |
| App sleeping when shared | Deployment phase (post-deploy) | Keep-alive Actions workflow running; app awake after 24h |
| Dev deps in requirements.txt | Deployment phase (pre-deploy) | No pytest in Streamlit Cloud build log |
| python-pptx / matplotlib missing | Deployment phase | End-to-end deck generation works on Cloud |
| API called on every demo click | Demo Landing phase | Second demo click returns instantly (cached) |
| File uploader buried | Demo Landing phase | Recruiter can initiate demo within 5s of page load |
| Skills section lacks rationale | Skills Showcase phase | Each item has one-sentence decision rationale |
| Template download corrupt | Data Template phase | Downloaded `.xlsx` opens without Excel repair prompt |

---

## Phase-Specific Warnings (v1.0)

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Excel parsing | Formula cells returning None | Use `data_only=True`; validate all required rows non-null before continuing |
| Excel parsing | Merged cell headers | Prohibit merges in template spec; detect and skip in parser |
| Excel parsing | Row label naming variations | LABEL_ALIASES dict with fuzzy matching |
| Excel parsing | Sign convention errors | Document expected signs; assert positive revenue |
| Metric computation | Wrong sign in EBITDA/margin calculations | Compute from Operating Income + D&A; add unit tests for known values |
| Slide template setup | Layout index brittleness | Name-based layout lookup; `verify_template()` at startup |
| Chart generation | Waterfall not in python-pptx | Matplotlib stacked-bar waterfall from day one |
| Chart generation | Blurry charts | 150+ DPI save; `bbox_inches='tight'`; BytesIO not temp file |
| Chart generation | Inconsistent brand colors | Single `CHART_STYLE` dict applied via `rcParams`; never inline colors |
| LLM integration | Generic non-consulting language | System prompt with persona, one-shot example, insight-first instruction |
| LLM integration | JSON wrapped in code fences | Strip markdown fences before `json.loads()`; or use tool-use API |
| LLM integration | Token limits on full-deck call | Concise output schema (title + 2-3 short bullets); validate response completeness |
| Streamlit UI | UploadedFile is not a path | Accept `Union[str, BinaryIO]` in core parser |
| Streamlit UI | BytesIO not reset before download | `buf.seek(0)` after every `prs.save(buf)` |
| Streamlit UI | Multiple LLM calls on rerun | Button-gated generation; cache result in `session_state` |
| Streamlit UI | Temp file disappears mid-processing | Never write to temp files; pass BytesIO throughout |

---

## Sources

### v1.0 Sources
Training-data knowledge of openpyxl, python-pptx, matplotlib, anthropic SDK, Streamlit documented behaviors. MEDIUM confidence — validate against current official docs.
- python-pptx: https://python-pptx.readthedocs.io/en/latest/
- openpyxl: https://openpyxl.readthedocs.io/en/stable/
- Anthropic API: https://docs.anthropic.com/
- Streamlit: https://docs.streamlit.io/

### v1.1 Sources (verified 2026-03-10)
- [Streamlit Community Cloud — Status and Limitations](https://docs.streamlit.io/deploy/streamlit-community-cloud/status)
- [Streamlit Community Cloud — Secrets Management](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Streamlit Community Cloud — App Dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies)
- [Streamlit — st.download_button docs](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button)
- [Streamlit — Button behavior and examples](https://docs.streamlit.io/develop/concepts/design/buttons)
- [Streamlit blog — 8 tips for securely using API keys](https://blog.streamlit.io/8-tips-for-securely-using-api-keys/)
- [Streamlit blog — Common app problems: Resource limits](https://blog.streamlit.io/common-app-problems-resource-limits/)
- [Anthropic — API Key Best Practices](https://support.claude.com/en/articles/9767949-api-key-best-practices-keeping-your-keys-safe-and-secure)
- [Anthropic — Rate limits](https://docs.anthropic.com/en/api/rate-limits)
- [Streamlit community — Download button reloads app and results output is gone](https://discuss.streamlit.io/t/download-button-reloads-app-and-results-output-is-gone-and-need-to-re-run/51467)
- [Streamlit community — App sleeping behavior](https://discuss.streamlit.io/t/how-to-prevent-the-app-enter-the-sleep-mode/87959)
- [GitHub issue — st.download_button should not rerun entire page](https://github.com/streamlit/streamlit/issues/3832)

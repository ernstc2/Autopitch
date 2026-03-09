# Domain Pitfalls

**Domain:** Python Excel-to-PowerPoint financial deck generator with AI narrative
**Project:** Autopitch
**Researched:** 2026-03-09
**Confidence note:** External search tools unavailable in this session. All findings are based on documented library behaviors from training data (openpyxl, python-pptx, matplotlib, anthropic SDK, Streamlit). Confidence levels assigned per claim. Validate critical items against current official docs before acting.

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

## Phase-Specific Warnings

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

**Confidence note:** All findings in this document are based on training-data knowledge of:
- `openpyxl` library documentation and known behaviors (data_only mode, merged cells, formula caching)
- `python-pptx` library documentation and known limitations (chart type support, placeholder indexing, layout naming)
- `matplotlib` embedding patterns in python-pptx (standard workaround for unsupported chart types)
- Anthropic Claude API behavior (JSON wrapping, output token limits, prompt engineering for structured output)
- Streamlit execution model (reactive reruns, UploadedFile type, session_state)

**Overall confidence:** MEDIUM — these are well-established library behaviors that are stable across versions. The specific behaviors described (e.g., formula caching, waterfall chart absence, code fence wrapping) are consistent across multiple documented sources from training data. Validate against current official docs before treating any item as authoritative:
- python-pptx: https://python-pptx.readthedocs.io/en/latest/
- openpyxl: https://openpyxl.readthedocs.io/en/stable/
- Anthropic API: https://docs.anthropic.com/
- Streamlit: https://docs.streamlit.io/

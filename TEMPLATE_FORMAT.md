# Autopitch Excel Input Template Format

## 1. Overview

This document describes the Excel workbook format accepted by Autopitch as input. The workbook is the single source of truth for all financial data; the pipeline parses it, validates it, and computes all metrics from it. Anyone preparing financial data for use with Autopitch — analysts, founders, or demo data maintainers — should read this document before creating or editing the workbook.

The template is designed to be filled in directly by a human in Excel or Google Sheets (exported to .xlsx). Programmatically generated files are also supported but require special handling (see Section 9).

---

## 2. Sheet Names

The workbook must contain exactly three sheets with these names (case-sensitive, spacing-exact):

| Sheet Name        | Contents                         |
|-------------------|----------------------------------|
| `P&L`             | Income statement line items      |
| `Balance Sheet`   | Balance sheet line items         |
| `Cash Flow`       | Cash flow statement line items   |

If any of these sheets is absent or misspelled, the parser raises a `ValidationError` before any data is read. Additional sheets (e.g., cover page, notes) are ignored.

---

## 3. Column Layout

Each sheet uses the following column structure:

| Column | Contents                              | Example           |
|--------|---------------------------------------|-------------------|
| A      | Row label (line item name)            | `Revenue`         |
| B      | First fiscal year value               | `394328`          |
| C      | Second fiscal year value              | `383285`          |
| D      | Third fiscal year value (if present)  | `391035`          |
| ...    | Additional years, one column each     |                   |

**Row 1 is the header row.** Cell A1 should be left blank or contain a sheet title. Cells B1, C1, D1, ... must contain fiscal year labels in the format `FYXXXX` (e.g., `FY2022`, `FY2023`, `FY2024`).

**All years must be ordered chronologically left to right** (oldest to newest). The parser reads year order from the header row and preserves it downstream.

---

## 4. Multi-Year Support

- **Minimum:** 2 fiscal years (required for growth and return metrics that need a prior year)
- **Maximum:** 5 fiscal years
- **Consecutive years required:** The parser does not interpolate missing years. If FY2021 and FY2023 are present but FY2022 is absent, metrics that require consecutive years will produce `None` for the affected periods.

Year labels must match the `FYXXXX` pattern exactly. Labels like `2022`, `FY22`, or `FY 2022` (with a space) will not be recognized and will cause a validation warning or error.

---

## 5. Sign Convention

**ALL values must be entered as positive numbers.**

This is the locked sign convention for this template. Revenue is positive. COGS is positive. Operating expenses are positive. Capital expenditures are positive. The formulas in the metrics engine apply the correct arithmetic signs internally.

| Incorrect                          | Correct                            |
|------------------------------------|------------------------------------|
| COGS = -223546 (entered negative)  | COGS = 223546 (entered positive)   |
| CapEx = -10708 (entered negative)  | CapEx = 10708 (entered positive)   |
| Net Income = -99803 (a loss)       | Net Income = 99803 (entered positive, loss handled separately) |

**Entering costs as negative numbers will produce incorrect margin calculations** (e.g., gross margin will appear > 100%) and trigger validation errors. The validator checks that all required row values are non-negative.

---

## 6. Required Row Labels Per Sheet

The following row labels must appear in Column A of each sheet. Labels are case-sensitive. The label must appear exactly as shown; leading/trailing whitespace is stripped, but internal spacing and capitalization must match.

### P&L Sheet

| Required Label                  | Notes                                                    |
|---------------------------------|----------------------------------------------------------|
| `Revenue`                       | Top-line revenue / net sales                             |
| `COGS`                          | Cost of goods sold / cost of revenue                     |
| `Operating Income`              | Also called EBIT (before D&A add-back for EBITDA)        |
| `Depreciation & Amortization`   | Used to compute EBITDA = Operating Income + D&A          |
| `Net Income`                    | Bottom-line net profit or loss                           |

### Balance Sheet Sheet

| Required Label                  | Notes                                                    |
|---------------------------------|----------------------------------------------------------|
| `Current Assets`                | Total current assets                                     |
| `Current Liabilities`           | Total current liabilities                                |
| `Total Assets`                  | Total assets (current + non-current)                     |
| `Total Debt`                    | Interest-bearing debt; used for D/E ratio                |
| `Total Shareholders Equity`     | Book value of equity; used for D/E, ROE, ROA             |

### Cash Flow Sheet

| Required Label                  | Notes                                                    |
|---------------------------------|----------------------------------------------------------|
| `Operating Cash Flow`           | Net cash from operating activities                       |
| `Capital Expenditures`          | Cash spent on property, plant, and equipment (positive)  |

If any required label is missing from its sheet, a `ValidationError` is raised listing all missing labels before any metric is computed.

---

## 7. Optional Row Labels

These rows may be present and will be read if found, but their absence does not trigger an error. The parser stores them in the `rows` dict alongside required rows and they are available to future metric extensions.

### P&L (optional)
- `Gross Profit`
- `EBITDA`
- `Tax Expense`
- `Interest Expense`

### Balance Sheet (optional)
- `Cash & Equivalents`
- `Inventory`
- `Accounts Receivable`
- `Accounts Payable`
- `Long-Term Debt`
- `Short-Term Debt`

### Cash Flow (optional)
- `Investing Cash Flow`
- `Financing Cash Flow`
- `Net Change in Cash`

---

## 8. Apple Demo Data and FY Label Convention

The demo file (`demo/apple_financials.xlsx`) uses Apple fiscal year labels. Apple's fiscal year ends in late September, not December 31.

| Label  | Period Covered                          |
|--------|-----------------------------------------|
| FY2020 | October 2019 – September 2020           |
| FY2021 | October 2020 – September 2021           |
| FY2022 | October 2021 – September 2022           |
| FY2023 | October 2022 – September 2023           |
| FY2024 | October 2023 – September 2024           |

Values in the demo file are sourced from Apple's annual reports (10-K filings). Line item names have been relabeled from 10-K conventions (e.g., "Net sales" → "Revenue", "Cost of sales" → "COGS") to match the canonical template labels above. The underlying numbers are unchanged.

---

## 9. Formula Cells Warning

The workbook must be saved in Excel with all formula cells evaluated and cached. Autopitch uses `openpyxl` with `data_only=True`, which reads the last cached value — not the formula itself.

**If a cell contains a formula that has never been evaluated** (e.g., the file was generated programmatically by a script that wrote formula strings but never opened the file in Excel), `openpyxl` will read the value as `None`. This will cause the parser to treat those cells as missing data and raise validation errors.

To avoid this: open the file in Excel and save it before passing it to Autopitch. This forces Excel to evaluate all formulas and cache the results.

---

## 10. Merged Cells Prohibition

Column A must not contain merged cells. The parser reads row labels by iterating Column A cells one row at a time; merged cells cause the label to appear in only the first cell of the merge, with subsequent cells returning `None`.

**Do not merge Column A cells** for section headers or grouping. If you want visual section headers (e.g., "Operating Expenses"), use a plain text row with no values in the year columns — the parser will ignore rows with no numeric values.

Merged cells in the year-value columns (B onward) are also not supported and will cause incorrect values to be read for affected rows.

from __future__ import annotations

from autopitch.models import FinancialData, ValidationError, ValidationResult

REQUIRED_ROWS = {
    "P&L": ["Revenue", "COGS", "Operating Income", "Depreciation & Amortization", "Net Income"],
    "Balance Sheet": ["Current Assets", "Current Liabilities", "Total Assets", "Total Debt", "Total Shareholders Equity"],
    "Cash Flow": ["Operating Cash Flow", "Capital Expenditures"],
}

OPTIONAL_ROWS = {
    "P&L": ["Gross Profit", "EBITDA", "Tax Expense", "Interest Expense"],
    "Balance Sheet": ["Inventory", "Accounts Receivable", "Accounts Payable", "Long-term Debt", "Short-term Debt"],
    "Cash Flow": ["Investing Activities", "Financing Activities"],
}

SHEET_TO_STATEMENT = {
    "P&L": "pl",
    "Balance Sheet": "balance_sheet",
    "Cash Flow": "cash_flow",
}


def validate(data: FinancialData) -> ValidationResult:
    """Validate a FinancialData object, collecting ALL errors before raising.

    Checks:
        1. Minimum 2 fiscal years present.
        2. All required rows exist in each statement.
        3. Required rows have no null values.
        4. Revenue values are all positive (sign convention).
        5. Optional missing rows generate warnings (not errors).

    Returns:
        ValidationResult with empty errors list if all checks pass.

    Raises:
        ValidationError: If any errors were collected.
    """
    result = ValidationResult()

    # 1. Minimum year check
    n_years = len(data.pl.years)
    if n_years < 2:
        result.errors.append(
            f"P&L: Minimum 2 fiscal years required. Found {n_years}."
        )

    # 2 & 3. Required row presence and null-value checks
    for sheet_name, required_labels in REQUIRED_ROWS.items():
        statement = getattr(data, SHEET_TO_STATEMENT[sheet_name])
        for label in required_labels:
            if label not in statement.rows:
                result.errors.append(
                    f"{sheet_name}: '{label}' row not found. Expected in column A."
                )
            else:
                # Check for null values in present required rows
                null_years = [
                    year for year, val in statement.rows[label].items() if val is None
                ]
                if null_years:
                    null_list = ", ".join(null_years)
                    result.errors.append(
                        f"{sheet_name}: '{label}' has null values for years: {null_list}. "
                        f"Ensure file was saved in Excel with cached formula values."
                    )

    # 4. Sign convention: Revenue must be positive
    if "Revenue" in data.pl.rows:
        for year, val in data.pl.rows["Revenue"].items():
            if val is not None and val <= 0:
                result.errors.append(
                    f"P&L: 'Revenue' has non-positive value {val} in {year}. "
                    f"Sign convention requires all values to be entered as positive numbers."
                )

    # 5. Optional row warnings
    for sheet_name, optional_labels in OPTIONAL_ROWS.items():
        statement = getattr(data, SHEET_TO_STATEMENT[sheet_name])
        for label in optional_labels:
            if label not in statement.rows:
                result.warnings.append(
                    f"{sheet_name}: Optional row '{label}' not found — "
                    f"metric computation will proceed without it."
                )

    if result.errors:
        raise ValidationError(result.errors)

    return result

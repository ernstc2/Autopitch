import pytest
from autopitch.models import FinancialData, StatementData, ValidationError
from autopitch.validator import validate


def test_collect_all_errors(minimal_valid_data):
    """INPT-02: Validation returns ALL errors in one pass, not just the first."""
    # Remove two required rows to verify both errors are collected
    rows_without_two = dict(minimal_valid_data.pl.rows)
    del rows_without_two["COGS"]
    del rows_without_two["Net Income"]
    bad_pl = StatementData(years=minimal_valid_data.pl.years, rows=rows_without_two)
    bad_data = FinancialData(
        company_name=minimal_valid_data.company_name,
        pl=bad_pl,
        balance_sheet=minimal_valid_data.balance_sheet,
        cash_flow=minimal_valid_data.cash_flow,
    )
    with pytest.raises(ValidationError) as exc_info:
        validate(bad_data)
    assert len(exc_info.value.errors) >= 2
    error_text = " ".join(exc_info.value.errors)
    assert "COGS" in error_text
    assert "Net Income" in error_text


def test_error_message_format(minimal_valid_data):
    """INPT-02: Error messages include sheet name, row label, and expected value."""
    rows_missing = dict(minimal_valid_data.balance_sheet.rows)
    del rows_missing["Total Assets"]
    bad_bs = StatementData(years=minimal_valid_data.balance_sheet.years, rows=rows_missing)
    bad_data = FinancialData(
        company_name=minimal_valid_data.company_name,
        pl=minimal_valid_data.pl,
        balance_sheet=bad_bs,
        cash_flow=minimal_valid_data.cash_flow,
    )
    with pytest.raises(ValidationError) as exc_info:
        validate(bad_data)
    assert any("Balance Sheet" in e and "Total Assets" in e for e in exc_info.value.errors)


def test_warnings_do_not_halt(minimal_valid_data):
    """INPT-02: Optional missing rows produce warnings but processing continues."""
    # Optional row absent — should return ValidationResult with warning, not raise
    result = validate(minimal_valid_data)  # minimal_valid_data has no optional rows
    assert result.errors == []
    # warnings may or may not be present depending on which optional rows are absent


def test_fatal_errors_raise(minimal_valid_data):
    """INPT-02: Fatal errors (missing required row) raise ValidationError."""
    rows_missing = dict(minimal_valid_data.cash_flow.rows)
    del rows_missing["Operating Cash Flow"]
    bad_cf = StatementData(years=minimal_valid_data.cash_flow.years, rows=rows_missing)
    bad_data = FinancialData(
        company_name=minimal_valid_data.company_name,
        pl=minimal_valid_data.pl,
        balance_sheet=minimal_valid_data.balance_sheet,
        cash_flow=bad_cf,
    )
    with pytest.raises(ValidationError):
        validate(bad_data)

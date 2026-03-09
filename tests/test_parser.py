import pytest
from pathlib import Path


def test_three_sheet_parse():
    """INPT-01: Parser reads P&L, Balance Sheet, Cash Flow sheets."""
    pytest.fail("Not implemented — complete in plan 02")


def test_missing_sheet_error():
    """INPT-01: Parser raises ValidationError when a required sheet is absent."""
    pytest.fail("Not implemented — complete in plan 02")


def test_accepts_path():
    """INPT-03: parse_workbook accepts pathlib.Path input."""
    pytest.fail("Not implemented — complete in plan 02")


def test_accepts_binary_io():
    """INPT-03: parse_workbook accepts BinaryIO stream (Streamlit use case)."""
    pytest.fail("Not implemented — complete in plan 02")


def test_demo_file_loads():
    """INPT-04: demo/apple_financials.xlsx loads without ValidationError."""
    pytest.fail("Not implemented — complete in plan 04")

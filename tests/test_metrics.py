import pytest
from autopitch.metrics import compute_metrics
from autopitch.models import FinancialData, StatementData


def test_revenue_growth(apple_two_year_data):
    """METR-01: Revenue growth FY2022 = (394328 - 365817) / 365817 * 100 ≈ 7.79%"""
    m = compute_metrics(apple_two_year_data)
    assert "FY2021" not in m.revenue_growth  # no prior year for FY2021 in 2-year fixture
    assert abs(m.revenue_growth["FY2022"] - 7.79) < 0.1


def test_margins(apple_two_year_data):
    """METR-02: Gross, EBITDA, and net margins for FY2022."""
    m = compute_metrics(apple_two_year_data)
    assert abs(m.gross_margin["FY2022"] - 43.31) < 0.1
    assert abs(m.ebitda_margin["FY2022"] - 33.11) < 0.5  # wider tolerance for EBITDA
    assert abs(m.net_margin["FY2022"] - 25.31) < 0.1


def test_liquidity(apple_two_year_data):
    """METR-03: Working capital and current ratio for FY2022."""
    m = compute_metrics(apple_two_year_data)
    assert abs(m.working_capital["FY2022"] - (-18577)) < 1.0
    assert abs(m.current_ratio["FY2022"] - 0.879) < 0.01


def test_leverage_returns(apple_two_year_data):
    """METR-04: D/E, ROE, ROA for FY2022 (FY2021 is first year — ROE/ROA use average)."""
    m = compute_metrics(apple_two_year_data)
    assert abs(m.debt_to_equity["FY2022"] - 2.614) < 0.01
    assert "FY2021" not in m.roe  # FY2021 is first year, no prior year for average
    assert abs(m.roe["FY2022"] - 175.47) < 2.0  # wide tolerance — high ROE from low equity
    assert abs(m.roa["FY2022"] - 28.37) < 0.5


def test_free_cash_flow(apple_two_year_data):
    """METR-05: FCF = Operating CF - CapEx for each year."""
    m = compute_metrics(apple_two_year_data)
    assert abs(m.free_cash_flow["FY2021"] - (104038.0 - 11085.0)) < 1.0
    assert abs(m.free_cash_flow["FY2022"] - (122151.0 - 10708.0)) < 1.0


def test_negative_equity_returns_none():
    """METR-04: D/E returns None when equity is negative (Apple FY2023 scenario)."""
    data = FinancialData(
        company_name="Test",
        pl=StatementData(
            years=["FY2022", "FY2023"],
            rows={
                "Revenue": {"FY2022": 1000.0, "FY2023": 1100.0},
                "COGS": {"FY2022": 600.0, "FY2023": 640.0},
                "Operating Income": {"FY2022": 200.0, "FY2023": 220.0},
                "Depreciation & Amortization": {"FY2022": 50.0, "FY2023": 55.0},
                "Net Income": {"FY2022": 120.0, "FY2023": 130.0},
            }
        ),
        balance_sheet=StatementData(
            years=["FY2022", "FY2023"],
            rows={
                "Current Assets": {"FY2022": 500.0, "FY2023": 520.0},
                "Current Liabilities": {"FY2022": 300.0, "FY2023": 310.0},
                "Total Assets": {"FY2022": 900.0, "FY2023": 950.0},
                "Total Debt": {"FY2022": 200.0, "FY2023": 190.0},
                "Total Shareholders Equity": {"FY2022": 400.0, "FY2023": -50.0},  # negative!
            }
        ),
        cash_flow=StatementData(
            years=["FY2022", "FY2023"],
            rows={
                "Operating Cash Flow": {"FY2022": 180.0, "FY2023": 200.0},
                "Capital Expenditures": {"FY2022": 40.0, "FY2023": 45.0},
            }
        ),
    )
    m = compute_metrics(data)
    # D/E FY2023: denominator is -50 (negative equity) — must return None
    assert m.debt_to_equity.get("FY2023") is None
    # ROE FY2023: avg equity = (400 + -50)/2 = 175 > 0, so ROE is defined (not None)
    # The critical check is D/E returning None for negative equity

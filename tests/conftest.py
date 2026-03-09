import pytest
from autopitch.models import FinancialData, StatementData


@pytest.fixture
def apple_two_year_data():
    """Minimal two-year AAPL fixture for formula verification.
    Values sourced from Apple FY2021-FY2022 10-K filings.
    Verify against SEC EDGAR before treating as ground truth.
    """
    return FinancialData(
        company_name="Apple Inc.",
        pl=StatementData(
            years=["FY2021", "FY2022"],
            rows={
                "Revenue":                        {"FY2021": 365817.0, "FY2022": 394328.0},
                "COGS":                           {"FY2021": 212981.0, "FY2022": 223546.0},
                "Operating Income":               {"FY2021": 108949.0, "FY2022": 119437.0},
                "Depreciation & Amortization":    {"FY2021":  11284.0, "FY2022":  11104.0},
                "Net Income":                     {"FY2021":  94680.0, "FY2022":  99803.0},
            }
        ),
        balance_sheet=StatementData(
            years=["FY2021", "FY2022"],
            rows={
                "Current Assets":               {"FY2021": 134836.0, "FY2022": 135405.0},
                "Current Liabilities":          {"FY2021": 125481.0, "FY2022": 153982.0},
                "Total Assets":                 {"FY2021": 351002.0, "FY2022": 352755.0},
                "Total Debt":                   {"FY2021": 136522.0, "FY2022": 132480.0},
                "Total Shareholders Equity":    {"FY2021":  63090.0, "FY2022":  50672.0},
            }
        ),
        cash_flow=StatementData(
            years=["FY2021", "FY2022"],
            rows={
                "Operating Cash Flow":   {"FY2021": 104038.0, "FY2022": 122151.0},
                "Capital Expenditures":  {"FY2021":  11085.0, "FY2022":  10708.0},
            }
        ),
    )


@pytest.fixture
def minimal_valid_data():
    """Smallest valid FinancialData for parser/validator unit tests."""
    return FinancialData(
        company_name="Test Co",
        pl=StatementData(
            years=["FY2022", "FY2023"],
            rows={
                "Revenue":                       {"FY2022": 1000.0, "FY2023": 1100.0},
                "COGS":                          {"FY2022":  600.0, "FY2023":  640.0},
                "Operating Income":              {"FY2022":  200.0, "FY2023":  240.0},
                "Depreciation & Amortization":   {"FY2022":   50.0, "FY2023":   55.0},
                "Net Income":                    {"FY2022":  120.0, "FY2023":  145.0},
            }
        ),
        balance_sheet=StatementData(
            years=["FY2022", "FY2023"],
            rows={
                "Current Assets":            {"FY2022": 500.0, "FY2023": 520.0},
                "Current Liabilities":       {"FY2022": 300.0, "FY2023": 310.0},
                "Total Assets":              {"FY2022": 900.0, "FY2023": 950.0},
                "Total Debt":                {"FY2022": 200.0, "FY2023": 190.0},
                "Total Shareholders Equity": {"FY2022": 400.0, "FY2023": 450.0},
            }
        ),
        cash_flow=StatementData(
            years=["FY2022", "FY2023"],
            rows={
                "Operating Cash Flow":  {"FY2022": 180.0, "FY2023": 210.0},
                "Capital Expenditures": {"FY2022":  40.0, "FY2023":  45.0},
            }
        ),
    )

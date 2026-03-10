from __future__ import annotations

from autopitch.models import FinancialData, MetricsOutput


def _safe_div(numerator: float | None, denominator: float | None) -> float | None:
    """Return numerator/denominator or None if denominator is zero/None/negative for ratio safety."""
    if numerator is None or denominator is None or denominator == 0:
        return None
    return numerator / denominator


def _get(rows: dict[str, dict[str, float | None]], row_name: str, year: str) -> float | None:
    """Safely retrieve a value from a statement row dict."""
    row = rows.get(row_name)
    if row is None:
        return None
    return row.get(year)


def compute_metrics(data: FinancialData) -> MetricsOutput:
    """Compute all 9 KPIs from validated FinancialData and return a MetricsOutput.

    Sign convention: all input values are POSITIVE (costs entered positive, subtracted in formulas).
    """
    pl = data.pl.rows
    bs = data.balance_sheet.rows
    cf = data.cash_flow.rows
    years = data.pl.years  # ordered list, e.g. ["FY2020", "FY2021", "FY2022", ...]

    # -------------------------------------------------------------------------
    # METR-01: Revenue Growth (%) — year-over-year, starts from second year
    # -------------------------------------------------------------------------
    revenue_growth: dict[str, float | None] = {}
    for i in range(1, len(years)):
        yr = years[i]
        prev_yr = years[i - 1]
        rev = _get(pl, "Revenue", yr)
        rev_prev = _get(pl, "Revenue", prev_yr)
        if rev is not None and rev_prev is not None and rev_prev != 0:
            revenue_growth[yr] = (rev - rev_prev) / rev_prev * 100
        else:
            revenue_growth[yr] = None

    # -------------------------------------------------------------------------
    # METR-02: Margins (%) — all years
    # -------------------------------------------------------------------------
    gross_margin: dict[str, float | None] = {}
    ebitda_margin: dict[str, float | None] = {}
    net_margin: dict[str, float | None] = {}

    for yr in years:
        rev = _get(pl, "Revenue", yr)

        # Gross margin = (Revenue - COGS) / Revenue * 100
        cogs = _get(pl, "COGS", yr)
        if rev is not None and cogs is not None and rev != 0:
            gross_margin[yr] = (rev - cogs) / rev * 100
        else:
            gross_margin[yr] = None

        # EBITDA margin = (Operating Income + D&A) / Revenue * 100
        op_income = _get(pl, "Operating Income", yr)
        da = _get(pl, "Depreciation & Amortization", yr)
        if rev is not None and op_income is not None and da is not None and rev != 0:
            ebitda_margin[yr] = (op_income + da) / rev * 100
        else:
            ebitda_margin[yr] = None

        # Net margin = Net Income / Revenue * 100
        net_income = _get(pl, "Net Income", yr)
        if rev is not None and net_income is not None and rev != 0:
            net_margin[yr] = net_income / rev * 100
        else:
            net_margin[yr] = None

    # -------------------------------------------------------------------------
    # METR-03: Liquidity — all years
    # -------------------------------------------------------------------------
    working_capital: dict[str, float | None] = {}
    current_ratio: dict[str, float | None] = {}

    for yr in years:
        curr_assets = _get(bs, "Current Assets", yr)
        curr_liab = _get(bs, "Current Liabilities", yr)

        # Working capital = Current Assets - Current Liabilities
        if curr_assets is not None and curr_liab is not None:
            working_capital[yr] = curr_assets - curr_liab
        else:
            working_capital[yr] = None

        # Current ratio = Current Assets / Current Liabilities
        current_ratio[yr] = _safe_div(curr_assets, curr_liab)

    # -------------------------------------------------------------------------
    # METR-04: Leverage and Returns
    # D/E and debt_to_equity — all years; ROE and ROA start from second year
    # -------------------------------------------------------------------------
    debt_to_equity: dict[str, float | None] = {}

    for yr in years:
        total_debt = _get(bs, "Total Debt", yr)
        equity = _get(bs, "Total Shareholders Equity", yr)

        # Guard: if equity <= 0, return None
        if equity is None or equity <= 0:
            debt_to_equity[yr] = None
        else:
            debt_to_equity[yr] = _safe_div(total_debt, equity)

    roe: dict[str, float | None] = {}
    roa: dict[str, float | None] = {}

    for i in range(1, len(years)):
        yr = years[i]
        prev_yr = years[i - 1]

        net_income = _get(pl, "Net Income", yr)

        # ROE = Net Income / Average Equity * 100
        equity_yr = _get(bs, "Total Shareholders Equity", yr)
        equity_prev = _get(bs, "Total Shareholders Equity", prev_yr)
        if equity_yr is not None and equity_prev is not None:
            avg_equity = (equity_yr + equity_prev) / 2
            if avg_equity <= 0:
                roe[yr] = None
            else:
                roe[yr] = _safe_div(net_income, avg_equity)
                if roe[yr] is not None:
                    roe[yr] = roe[yr] * 100
        else:
            roe[yr] = None

        # ROA = Net Income / Average Total Assets * 100
        assets_yr = _get(bs, "Total Assets", yr)
        assets_prev = _get(bs, "Total Assets", prev_yr)
        if assets_yr is not None and assets_prev is not None:
            avg_assets = (assets_yr + assets_prev) / 2
            roa[yr] = _safe_div(net_income, avg_assets)
            if roa[yr] is not None:
                roa[yr] = roa[yr] * 100
        else:
            roa[yr] = None

    # -------------------------------------------------------------------------
    # METR-05: Free Cash Flow = Operating Cash Flow - Capital Expenditures
    # -------------------------------------------------------------------------
    free_cash_flow: dict[str, float | None] = {}

    for yr in years:
        op_cf = _get(cf, "Operating Cash Flow", yr)
        capex = _get(cf, "Capital Expenditures", yr)
        if op_cf is not None and capex is not None:
            free_cash_flow[yr] = op_cf - capex
        else:
            free_cash_flow[yr] = None

    return MetricsOutput(
        years=list(years),
        revenue_growth=revenue_growth,
        gross_margin=gross_margin,
        ebitda_margin=ebitda_margin,
        net_margin=net_margin,
        working_capital=working_capital,
        current_ratio=current_ratio,
        debt_to_equity=debt_to_equity,
        roe=roe,
        roa=roa,
        free_cash_flow=free_cash_flow,
    )

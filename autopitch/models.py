from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict


class StatementData(BaseModel):
    model_config = ConfigDict(frozen=True)

    years: list[str]                          # ordered: ["FY2020", "FY2021", ...]
    rows: dict[str, dict[str, float | None]]  # {"Revenue": {"FY2020": 274515.0, ...}}


class FinancialData(BaseModel):
    model_config = ConfigDict(frozen=True)

    company_name: str
    pl: StatementData
    balance_sheet: StatementData
    cash_flow: StatementData


class MetricsOutput(BaseModel):
    years: list[str]
    revenue_growth: dict[str, float | None]    # FY2021-FY2024 only (needs prior year)
    gross_margin: dict[str, float | None]
    ebitda_margin: dict[str, float | None]
    net_margin: dict[str, float | None]
    working_capital: dict[str, float | None]
    current_ratio: dict[str, float | None]
    debt_to_equity: dict[str, float | None]    # None when equity <= 0
    roe: dict[str, float | None]               # FY2021-FY2024 only; None when avg equity <= 0
    roa: dict[str, float | None]               # FY2021-FY2024 only
    free_cash_flow: dict[str, float | None]


@dataclass
class ValidationResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ValidationError(Exception):
    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))

"""Tests for autopitch.models — run RED before models.py exists, GREEN after."""
import json
import pytest


def test_imports():
    """All six names must be importable from autopitch.models."""
    from autopitch.models import (
        FinancialData,
        StatementData,
        MetricsOutput,
        ValidationResult,
        ValidationError,
    )


def test_statement_data_frozen():
    from autopitch.models import StatementData
    sd = StatementData(years=["FY2022"], rows={"Revenue": {"FY2022": 100.0}})
    with pytest.raises(Exception):
        sd.years = ["FY2023"]  # type: ignore


def test_financial_data_structure():
    from autopitch.models import FinancialData, StatementData
    fd = FinancialData(
        company_name="Test",
        pl=StatementData(years=["FY2022"], rows={"Revenue": {"FY2022": 100.0}}),
        balance_sheet=StatementData(years=["FY2022"], rows={}),
        cash_flow=StatementData(years=["FY2022"], rows={}),
    )
    assert fd.company_name == "Test"
    assert fd.pl.years == ["FY2022"]


def test_metrics_output_json_serializable():
    from autopitch.models import MetricsOutput
    mo = MetricsOutput(
        years=["FY2022"],
        revenue_growth={},
        gross_margin={"FY2022": 43.0},
        ebitda_margin={},
        net_margin={},
        working_capital={},
        current_ratio={},
        debt_to_equity={"FY2022": None},
        roe={},
        roa={},
        free_cash_flow={},
    )
    result = json.dumps(mo.model_dump(mode="json"))
    assert isinstance(result, str)


def test_validation_result_dataclass():
    from autopitch.models import ValidationResult
    vr = ValidationResult(errors=["e1"], warnings=["w1"])
    assert vr.errors == ["e1"]
    assert vr.warnings == ["w1"]


def test_validation_error_stores_list():
    from autopitch.models import ValidationError
    ve = ValidationError(["e1", "e2"])
    assert ve.errors == ["e1", "e2"]
    assert "e1" in str(ve)
    assert "e2" in str(ve)


def test_metrics_output_none_values():
    """None values in dict fields must survive JSON round-trip."""
    from autopitch.models import MetricsOutput
    import json
    mo = MetricsOutput(
        years=["FY2022", "FY2023"],
        revenue_growth={"FY2023": None},
        gross_margin={"FY2022": 43.31, "FY2023": None},
        ebitda_margin={},
        net_margin={},
        working_capital={},
        current_ratio={},
        debt_to_equity={"FY2022": None},
        roe={},
        roa={},
        free_cash_flow={},
    )
    dumped = mo.model_dump(mode="json")
    assert dumped["gross_margin"]["FY2022"] == pytest.approx(43.31)
    assert dumped["gross_margin"]["FY2023"] is None
    # Must be JSON serializable
    json.dumps(dumped)

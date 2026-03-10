"""
Failing test stubs for CHRT-01..05.
All tests are skipped until autopitch.charts is implemented.
"""
import io
import pytest
from PIL import Image

try:
    from autopitch.charts import bar_chart, line_chart, waterfall_chart, kpi_scorecard
    _CHARTS_AVAILABLE = True
except ImportError:
    _CHARTS_AVAILABLE = False

pytestmark = pytest.mark.skipif(not _CHARTS_AVAILABLE, reason="autopitch.charts not yet implemented")


def test_bar_chart_returns_png():
    """CHRT-01: bar_chart returns a non-empty BytesIO containing a valid PNG."""
    years = ["FY2021", "FY2022", "FY2023"]
    values = [100.0, 120.0, 140.0]
    result = bar_chart(years, values, title="Revenue", ylabel="$M")
    assert isinstance(result, io.BytesIO)
    result.seek(0)
    data = result.read()
    assert len(data) > 0
    result.seek(0)
    img = Image.open(result)
    assert img.format == "PNG"


def test_line_chart_multi_series():
    """CHRT-02: line_chart with multiple series returns a non-empty valid PNG."""
    years = ["FY2021", "FY2022", "FY2023"]
    series_dict = {
        "Gross Margin": [40.0, 42.0, 43.0],
        "EBITDA Margin": [20.0, 21.0, 22.0],
        "Net Margin": [10.0, 11.0, 12.0],
    }
    result = line_chart(years, series_dict, title="Margin Trends", ylabel="%")
    assert isinstance(result, io.BytesIO)
    result.seek(0)
    data = result.read()
    assert len(data) > 0
    result.seek(0)
    img = Image.open(result)
    assert img.format == "PNG"


def test_waterfall_chart():
    """CHRT-03: waterfall_chart returns a non-empty valid PNG."""
    labels = ["Revenue", "COGS", "Gross Profit", "OpEx", "EBIT"]
    values = [1000.0, -600.0, 400.0, -150.0, 250.0]
    result = waterfall_chart(labels, values, title="P&L Waterfall")
    assert isinstance(result, io.BytesIO)
    result.seek(0)
    data = result.read()
    assert len(data) > 0
    result.seek(0)
    img = Image.open(result)
    assert img.format == "PNG"


def test_chart_dpi():
    """CHRT-04: bar_chart output is rendered at 150 DPI."""
    years = ["FY2021", "FY2022"]
    values = [100.0, 120.0]
    result = bar_chart(years, values, title="Test", ylabel="$M")
    result.seek(0)
    img = Image.open(result)
    dpi = img.info.get("dpi")
    # Accept either exact tuple or values within 1 unit of 150 due to float rounding
    if dpi is not None:
        assert abs(dpi[0] - 150.0) < 1.0 and abs(dpi[1] - 150.0) < 1.0, (
            f"Expected DPI ~150, got {dpi}"
        )
    else:
        # If dpi not stored in PNG metadata, verify image dimensions are consistent
        # with 150 DPI (e.g., a 10-inch-wide figure → ~1500px wide)
        width_px, _ = img.size
        assert width_px >= 900, f"Expected width >= 900px for 150 DPI, got {width_px}"


def test_kpi_scorecard():
    """CHRT-05: kpi_scorecard returns a non-empty valid PNG."""
    metrics_dict = {
        "Revenue Growth": "10.0%",
        "Gross Margin": "42.0%",
        "EBITDA Margin": "22.0%",
        "Net Margin": "12.0%",
        "Free Cash Flow": "$250M",
    }
    result = kpi_scorecard(metrics_dict, title="KPI Scorecard")
    assert isinstance(result, io.BytesIO)
    result.seek(0)
    data = result.read()
    assert len(data) > 0
    result.seek(0)
    img = Image.open(result)
    assert img.format == "PNG"

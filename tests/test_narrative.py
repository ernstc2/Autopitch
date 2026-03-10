"""Tests for autopitch.narrative — NARR-01, NARR-02, NARR-03, NARR-05.

All four tests must fail (ImportError) before narrative.py is implemented (TDD Wave 0).
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from autopitch.narrative import NarrativeOutput, generate_narrative


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MOCK_JSON = json.dumps(
    {
        "exec_summary_title": "Revenue surged 18% driven by Services mix shift",
        "exec_summary_bullets": ["Bullet A", "Bullet B", "Bullet C"],
        "pl_revenue_title": "Revenue growth accelerated to 18% in FY2024",
        "pl_margin_title": "Gross margin held at 43% despite input cost pressure",
        "pl_bridge_title": "Net income expanded as operating leverage kicked in",
        "pl_bullets": ["Bullet A", "Bullet B"],
        "bs_assets_title": "Asset base grew 12% with services infrastructure leading",
        "bs_wc_title": "Working capital surplus signals strong short-term liquidity",
        "bs_leverage_title": "Net cash position reflects conservative balance sheet management",
        "bs_bullets": ["Bullet A", "Bullet B"],
        "cf_fcf_title": "Free cash flow reached record high of $100B in FY2024",
        "cf_trend_title": "OCF growth outpaced capex expansion for third consecutive year",
        "cf_bullets": ["Bullet A", "Bullet B"],
        "kpi_title": "KPI Scorecard — strong across all profitability dimensions",
    }
)


def _make_mock_response() -> MagicMock:
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = MOCK_JSON
    return mock_response


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_fallback_no_api_key(minimal_valid_data, metrics_from_minimal, monkeypatch):
    """NARR-05: No API key → NarrativeOutput with placeholders, no exception raised."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    result = generate_narrative(minimal_valid_data, metrics_from_minimal)

    assert isinstance(result, NarrativeOutput)
    assert isinstance(result.exec_summary_title, str)
    assert len(result.exec_summary_title) > 0


def test_narrative_titles_not_generic(minimal_valid_data, metrics_from_minimal, monkeypatch):
    """NARR-01: With mocked API, all title fields populated from the JSON response."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    with patch("autopitch.narrative.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_response()

        result = generate_narrative(minimal_valid_data, metrics_from_minimal)

    assert isinstance(result, NarrativeOutput)
    assert result.exec_summary_title == "Revenue surged 18% driven by Services mix shift"
    assert result.pl_revenue_title == "Revenue growth accelerated to 18% in FY2024"
    assert result.pl_margin_title == "Gross margin held at 43% despite input cost pressure"
    assert result.pl_bridge_title == "Net income expanded as operating leverage kicked in"
    assert result.bs_assets_title == "Asset base grew 12% with services infrastructure leading"
    assert result.bs_wc_title == "Working capital surplus signals strong short-term liquidity"
    assert result.bs_leverage_title == "Net cash position reflects conservative balance sheet management"
    assert result.cf_fcf_title == "Free cash flow reached record high of $100B in FY2024"
    assert result.cf_trend_title == "OCF growth outpaced capex expansion for third consecutive year"
    assert result.kpi_title == "KPI Scorecard — strong across all profitability dimensions"


def test_narrative_bullets_count(minimal_valid_data, metrics_from_minimal, monkeypatch):
    """NARR-02: With mocked API, bullet lists have >= 2 items per section."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    with patch("autopitch.narrative.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_response()

        result = generate_narrative(minimal_valid_data, metrics_from_minimal)

    assert len(result.exec_summary_bullets) >= 2
    assert len(result.pl_bullets) >= 2
    assert len(result.bs_bullets) >= 2
    assert len(result.cf_bullets) >= 2


def test_single_api_call(minimal_valid_data, metrics_from_minimal, monkeypatch):
    """NARR-03: Exactly one call to messages.create regardless of slide count."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    with patch("autopitch.narrative.Anthropic") as mock_anthropic_cls:
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = _make_mock_response()

        generate_narrative(minimal_valid_data, metrics_from_minimal)

    assert mock_client.messages.create.call_count == 1

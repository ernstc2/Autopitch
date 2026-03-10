"""Narrative generation module — NarrativeOutput model and generate_narrative().

Exports:
    NarrativeOutput: Pydantic v2 frozen model holding all slide title and bullet fields.
    generate_narrative: Single-call Claude API function that returns a NarrativeOutput.

NARR-05: If ANTHROPIC_API_KEY is absent, generate_narrative() returns NarrativeOutput()
(all placeholder defaults) without raising any exception.
"""
from __future__ import annotations

import json
import os

from anthropic import Anthropic
from pydantic import BaseModel, ConfigDict

from autopitch.models import FinancialData, MetricsOutput


# ---------------------------------------------------------------------------
# NarrativeOutput model
# ---------------------------------------------------------------------------


class NarrativeOutput(BaseModel):
    """Typed container for all AI-generated slide titles and bullet commentary.

    All fields have placeholder string defaults so NarrativeOutput() can be
    returned as a safe fallback when the API is unavailable (NARR-05).
    """

    model_config = ConfigDict(frozen=True)

    # Executive summary slide
    exec_summary_title: str = "Executive Summary"
    exec_summary_bullets: list[str] = ["Revenue", "Margins", "Free Cash Flow"]

    # P&L slides
    pl_revenue_title: str = "P&L | Revenue Trends"
    pl_margin_title: str = "P&L | Margin Analysis"
    pl_bridge_title: str = "P&L | Earnings Bridge"
    pl_bullets: list[str] = ["Revenue trends", "Margin profile", "Net income"]

    # Balance sheet slides
    bs_assets_title: str = "Balance Sheet | Asset Composition"
    bs_wc_title: str = "Balance Sheet | Working Capital"
    bs_leverage_title: str = "Balance Sheet | Leverage"
    bs_bullets: list[str] = ["Asset base", "Liquidity position", "Debt structure"]

    # Cash flow slides
    cf_fcf_title: str = "Cash Flow | OCF vs FCF"
    cf_trend_title: str = "Cash Flow | Trend"
    cf_bullets: list[str] = ["Operating cash flow", "Capex", "Free cash flow"]

    # KPI scorecard slide
    kpi_title: str = "KPI Scorecard"


# ---------------------------------------------------------------------------
# System prompt — consulting analyst persona with one-shot example (NARR-04)
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a senior financial analyst at a Big 4 consulting firm.
Your task is to write slide titles and commentary that reveal insight, not describe data.

Rules:
- Titles state a conclusion or trend (max 15 words)
- Bullets are forward-looking and analytical, not descriptive (2-3 per section, max 25 words each)
- No filler phrases ("It is worth noting that...", "The data shows...")
- Titles must name a specific number or percentage where available

<example>
Input metrics snippet: revenue_growth FY2023=18.3%, gross_margin FY2023=43.1%
Output:
{
  "pl_revenue_title": "Revenue accelerated 18% in FY2023 — services segment the primary driver",
  "pl_bullets": [
    "Services revenue outpaced hardware by 3x, structurally improving mix quality.",
    "Sustained high-single-digit growth trajectory warrants revisiting capacity expansion timeline.",
    "Geographic diversification masks a 6-point APAC deceleration worth monitoring."
  ]
}
</example>"""

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

_SCHEMA_KEYS = (
    "exec_summary_title",
    "exec_summary_bullets",
    "pl_revenue_title",
    "pl_margin_title",
    "pl_bridge_title",
    "pl_bullets",
    "bs_assets_title",
    "bs_wc_title",
    "bs_leverage_title",
    "bs_bullets",
    "cf_fcf_title",
    "cf_trend_title",
    "cf_bullets",
    "kpi_title",
)


def _build_prompt(data: FinancialData, metrics: MetricsOutput) -> str:
    """Serialise all computed metrics into a structured user message."""
    metrics_json = json.dumps(metrics.model_dump(mode="json"), indent=2)
    schema = {k: "..." for k in _SCHEMA_KEYS}
    # Override list keys with array notation so the model knows the shape
    for k in ("exec_summary_bullets", "pl_bullets", "bs_bullets", "cf_bullets"):
        schema[k] = ["...", "...", "..."]
    schema_str = json.dumps(schema, indent=2)

    return (
        f"<financial_metrics>\n{metrics_json}\n</financial_metrics>\n\n"
        "Note: All dollar values in the metrics above are in USD millions (e.g. 99360 = $99.4B).\n"
        "When citing specific values in titles or bullets, convert to billions (e.g. '$99B FCF').\n\n"
        "Generate insight-first titles and consulting-voice commentary for a financial deck.\n"
        f"Return ONLY a JSON object matching this schema:\n{schema_str}\n"
        "No markdown. No explanation. JSON only."
    )


def _parse_response(raw: str) -> NarrativeOutput:
    """Parse the model's raw text output into a NarrativeOutput.

    Strips markdown code fences if present. Falls back to NarrativeOutput()
    (all placeholder defaults) on any parse error.
    """
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]) if lines[-1].startswith("```") else "\n".join(lines[1:])
    try:
        data = json.loads(text)
        return NarrativeOutput(**data)
    except Exception:
        return NarrativeOutput()


def _placeholder_narrative(metrics: MetricsOutput) -> NarrativeOutput:
    """Return a NarrativeOutput with all placeholder defaults (NARR-05 fallback)."""
    return NarrativeOutput()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_narrative(data: FinancialData, metrics: MetricsOutput) -> NarrativeOutput:
    """Generate insight-first slide titles and consulting-voice bullets via Claude API.

    Makes exactly ONE call to messages.create per invocation (NARR-03).

    If ANTHROPIC_API_KEY is not set in the environment, returns NarrativeOutput()
    with all placeholder defaults — no exception is raised (NARR-05).

    Args:
        data: Parsed financial statements (FinancialData).
        metrics: Pre-computed financial metrics (MetricsOutput).

    Returns:
        NarrativeOutput with AI-generated or placeholder content.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _placeholder_narrative(metrics)

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_prompt(data, metrics)}],
    )
    return _parse_response(response.content[0].text)

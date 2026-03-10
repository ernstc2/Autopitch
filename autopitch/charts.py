"""
Chart generation module for Autopitch.

All public functions return io.BytesIO containing a valid PNG at 150 DPI.
Uses the Agg (non-interactive) backend — no display window opens.
"""
import matplotlib
matplotlib.use('Agg')  # Must be before any pyplot import

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import io

from autopitch.theme import (
    NAVY_HEX, TEAL_HEX, LIGHT_GRAY_HEX, DARK_GRAY_HEX,
    POSITIVE_HEX, NEGATIVE_HEX, FONT_HEADING, FONT_BODY,
)

# Module-level constants
DPI = 150
FIGSIZE_STANDARD = (10, 5.5)  # 16:9-ish for content area

# Font cascade: use Calibri when available, fall back to Arial then DejaVu Sans
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Calibri', 'Arial', 'DejaVu Sans'],
    'axes.titlesize': 14,
    'axes.labelsize': 10,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
})


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _apply_consulting_style(ax, fig):
    """Apply Big 4 chart style: remove top/right spines, gray gridlines, correct fonts."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(DARK_GRAY_HEX)
    ax.spines['bottom'].set_color(DARK_GRAY_HEX)
    ax.yaxis.grid(True, color=LIGHT_GRAY_HEX, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(colors=DARK_GRAY_HEX, labelsize=10)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontfamily(FONT_BODY)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')


def _to_bytesio(fig) -> io.BytesIO:
    """Save figure to an in-memory PNG buffer at DPI=150 and close the figure."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=DPI, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf


# ---------------------------------------------------------------------------
# Public chart functions
# ---------------------------------------------------------------------------

def bar_chart(years: list, values: list, title: str, ylabel: str) -> io.BytesIO:
    """CHRT-01: Column chart for revenue/expense trends.

    Args:
        years: List of period labels (e.g. ["FY2021", "FY2022", "FY2023"]).
        values: List of numeric values corresponding to each year.
        title: Chart title displayed above the figure.
        ylabel: Y-axis label.

    Returns:
        io.BytesIO containing a valid PNG at 150 DPI.
    """
    fig, ax = plt.subplots(figsize=FIGSIZE_STANDARD)
    bars = ax.bar(years, values, color=NAVY_HEX, width=0.5, zorder=3)
    # Accent the most-recent (last) bar in teal
    bars[-1].set_color(TEAL_HEX)
    ax.set_title(title, fontfamily=FONT_HEADING, fontsize=14, color=DARK_GRAY_HEX, pad=10)
    ax.set_ylabel(ylabel, fontfamily=FONT_BODY, fontsize=10, color=DARK_GRAY_HEX)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"${x / 1000:.0f}B")
    )
    _apply_consulting_style(ax, fig)
    return _to_bytesio(fig)


def line_chart(years: list, series: dict, title: str, ylabel: str, percent: bool = True) -> io.BytesIO:
    """CHRT-02: Line chart for margin trends or USD time-series (up to 3 series).

    Args:
        years: List of period labels.
        series: Dict mapping series name to list of values (up to 3 entries).
        title: Chart title.
        ylabel: Y-axis label.
        percent: If True (default), format Y-axis as percentage. If False, format as $B.

    Returns:
        io.BytesIO containing a valid PNG at 150 DPI.
    """
    colors = [NAVY_HEX, TEAL_HEX, DARK_GRAY_HEX]
    fig, ax = plt.subplots(figsize=FIGSIZE_STANDARD)
    for (name, vals), color in zip(series.items(), colors):
        ax.plot(years, vals, marker='o', label=name, color=color, linewidth=2)
    ax.set_title(title, fontfamily=FONT_HEADING, fontsize=14, color=DARK_GRAY_HEX, pad=10)
    ax.set_ylabel(ylabel, fontfamily=FONT_BODY, fontsize=10, color=DARK_GRAY_HEX)
    if percent:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    else:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x / 1000:.0f}B"))
    ax.legend(frameon=False, fontsize=9)
    _apply_consulting_style(ax, fig)
    return _to_bytesio(fig)


def waterfall_chart(labels: list, values: list, title: str, is_total: list | None = None) -> io.BytesIO:
    """CHRT-03: P&L bridge waterfall chart.

    Supports two bar types:
    - Total bars (is_total=True): solid bar from 0, NAVY_HEX.
    - Delta bars (is_total=False): floating bar between adjacent totals;
      positive deltas use POSITIVE_HEX, negative use NEGATIVE_HEX.

    Args:
        labels: Bar labels (e.g. ["Revenue", "- COGS", ..., "Net Income"]).
        values: Numeric values. Totals = absolute value; deltas = signed change.
        title: Chart title.
        is_total: Boolean list same length as labels. True = total bar. Defaults
                  to [True, False, ..., False, True] (first and last are totals).

    Returns:
        io.BytesIO containing a valid PNG at 150 DPI.
    """
    n = len(values)
    if is_total is None:
        is_total = [i == 0 or i == n - 1 for i in range(n)]

    bottoms = np.zeros(n)
    heights = np.zeros(n)
    colors = []
    current = 0.0

    for i in range(n):
        if is_total[i]:
            bottoms[i] = 0.0
            heights[i] = abs(values[i])
            current = float(values[i])
            colors.append(NAVY_HEX)
        else:
            delta = float(values[i])
            if delta < 0:
                # Deduction: bar hangs down from current level
                bottoms[i] = current + delta
                heights[i] = -delta
                colors.append(NEGATIVE_HEX)
            else:
                # Addition: bar rises from current level
                bottoms[i] = current
                heights[i] = delta
                colors.append(POSITIVE_HEX)
            current += delta

    fig, ax = plt.subplots(figsize=FIGSIZE_STANDARD)
    ax.bar(labels, heights, bottom=bottoms, color=colors, width=0.5, zorder=3)
    ax.set_title(title, fontfamily=FONT_HEADING, fontsize=14, color=DARK_GRAY_HEX, pad=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x / 1000:.0f}B"))
    _apply_consulting_style(ax, fig)
    return _to_bytesio(fig)


def kpi_scorecard(metrics: dict, title: str) -> io.BytesIO:
    """CHRT-05: KPI text grid — value (large, navy, bold) above label (small, gray).

    Grid layout: n_cols = min(5, len(metrics)), n_rows = ceil(len / n_cols).
    No axes or spines are drawn.

    Args:
        metrics: Dict mapping metric label to formatted value string
                 (e.g. {"Revenue Growth": "10.0%"}).
        title: Chart title displayed above the grid.

    Returns:
        io.BytesIO containing a valid PNG at 150 DPI.
    """
    import math

    items = list(metrics.items())
    n_cols = min(5, len(items))
    n_rows = math.ceil(len(items) / n_cols)

    fig, ax = plt.subplots(figsize=FIGSIZE_STANDARD)
    ax.axis('off')
    ax.set_title(title, fontfamily=FONT_HEADING, fontsize=14, color=DARK_GRAY_HEX, pad=10)

    col_w = 1.0 / n_cols
    row_h = 0.8 / n_rows

    for i, (label, value) in enumerate(items):
        col = i % n_cols
        row = i // n_cols
        x = col * col_w + col_w / 2
        y = 0.9 - row * row_h - row_h / 2

        # Value: large, navy, bold
        ax.text(
            x, y + 0.06, value,
            ha='center', va='center',
            fontsize=28, fontfamily=FONT_HEADING,
            color=NAVY_HEX, fontweight='bold',
            transform=ax.transAxes,
        )
        # Label: small, dark gray
        ax.text(
            x, y - 0.06, label,
            ha='center', va='center',
            fontsize=9, fontfamily=FONT_BODY,
            color=DARK_GRAY_HEX,
            transform=ax.transAxes,
        )
        # Subtle separator line below each KPI cell (using axes-coordinate plot)
        ax.plot(
            [col * col_w + 0.01, (col + 1) * col_w - 0.01],
            [y - 0.14, y - 0.14],
            color=LIGHT_GRAY_HEX, linewidth=1,
            transform=ax.transAxes,
        )

    fig.patch.set_facecolor('white')
    return _to_bytesio(fig)

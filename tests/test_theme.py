"""Structural tests for Streamlit theme configuration and app layout.

Covers VISL-01 (config.toml dark navy theme) and VISL-02 (wide layout in app.py).
All tests are file-level structural checks — no Streamlit runtime required.
"""

import tomllib
from pathlib import Path


CONFIG_TOML = Path(".streamlit/config.toml")
APP_PY = Path("app.py")


def _load_theme() -> dict:
    """Load and return the [theme] section from config.toml."""
    with CONFIG_TOML.open("rb") as fh:
        data = tomllib.load(fh)
    return data.get("theme", {})


def test_config_toml_exists():
    """VISL-01: .streamlit/config.toml must exist."""
    assert CONFIG_TOML.exists(), f"{CONFIG_TOML} does not exist"


def test_has_theme_section():
    """VISL-01: config.toml must contain a [theme] section."""
    with CONFIG_TOML.open("rb") as fh:
        data = tomllib.load(fh)
    assert "theme" in data, "config.toml missing [theme] section"


def test_primary_color_is_teal():
    """VISL-01: primaryColor must be #00838A (teal accent matching PPTX palette)."""
    theme = _load_theme()
    assert theme.get("primaryColor") == "#00838A", (
        f"primaryColor is {theme.get('primaryColor')!r}, expected '#00838A'"
    )


def test_base_is_dark():
    """VISL-01: base must be 'dark'."""
    theme = _load_theme()
    assert theme.get("base") == "dark", (
        f"base is {theme.get('base')!r}, expected 'dark'"
    )


def test_font_is_sans_serif():
    """VISL-01: font must be 'sans serif'."""
    theme = _load_theme()
    assert theme.get("font") == "sans serif", (
        f"font is {theme.get('font')!r}, expected 'sans serif'"
    )


def test_background_color():
    """VISL-01: backgroundColor must be #0a1628 (deep navy)."""
    theme = _load_theme()
    assert theme.get("backgroundColor") == "#0a1628", (
        f"backgroundColor is {theme.get('backgroundColor')!r}, expected '#0a1628'"
    )


def test_secondary_bg_color():
    """VISL-01: secondaryBackgroundColor must be #132238 (card navy)."""
    theme = _load_theme()
    assert theme.get("secondaryBackgroundColor") == "#132238", (
        f"secondaryBackgroundColor is {theme.get('secondaryBackgroundColor')!r}, "
        "expected '#132238'"
    )


def test_text_color():
    """VISL-01: textColor must be #e8edf4 (soft white)."""
    theme = _load_theme()
    assert theme.get("textColor") == "#e8edf4", (
        f"textColor is {theme.get('textColor')!r}, expected '#e8edf4'"
    )


def test_wide_layout_in_app():
    """VISL-02: app.py must contain st.set_page_config with layout='wide'."""
    source = APP_PY.read_text(encoding="utf-8")
    assert 'layout="wide"' in source, (
        "app.py does not contain layout=\"wide\" in st.set_page_config"
    )

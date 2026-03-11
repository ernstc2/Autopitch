"""Structural tests for Streamlit theme configuration and app layout.

Covers VISL-01 (config.toml navy theme) and VISL-02 (wide layout in app.py).
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


def test_primary_color_is_navy():
    """VISL-01: primaryColor must be #0a2540 (deep navy)."""
    theme = _load_theme()
    assert theme.get("primaryColor") == "#0a2540", (
        f"primaryColor is {theme.get('primaryColor')!r}, expected '#0a2540'"
    )


def test_base_is_light():
    """VISL-01: base must be 'light'."""
    theme = _load_theme()
    assert theme.get("base") == "light", (
        f"base is {theme.get('base')!r}, expected 'light'"
    )


def test_font_is_sans_serif():
    """VISL-01: font must be 'sans serif'."""
    theme = _load_theme()
    assert theme.get("font") == "sans serif", (
        f"font is {theme.get('font')!r}, expected 'sans serif'"
    )


def test_background_color():
    """VISL-01: backgroundColor must be #ffffff."""
    theme = _load_theme()
    assert theme.get("backgroundColor") == "#ffffff", (
        f"backgroundColor is {theme.get('backgroundColor')!r}, expected '#ffffff'"
    )


def test_secondary_bg_color():
    """VISL-01: secondaryBackgroundColor must be #f0f4f8."""
    theme = _load_theme()
    assert theme.get("secondaryBackgroundColor") == "#f0f4f8", (
        f"secondaryBackgroundColor is {theme.get('secondaryBackgroundColor')!r}, "
        "expected '#f0f4f8'"
    )


def test_text_color():
    """VISL-01: textColor must be #1a1a2e."""
    theme = _load_theme()
    assert theme.get("textColor") == "#1a1a2e", (
        f"textColor is {theme.get('textColor')!r}, expected '#1a1a2e'"
    )


def test_wide_layout_in_app():
    """VISL-02: app.py must contain st.set_page_config with layout='wide'."""
    source = APP_PY.read_text(encoding="utf-8")
    assert 'layout="wide"' in source, (
        "app.py does not contain layout=\"wide\" in st.set_page_config"
    )

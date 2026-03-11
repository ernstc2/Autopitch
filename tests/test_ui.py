"""Structural and unit tests for app.py UI patterns.

Tests verify that app.py contains the required structural patterns for:
- DEMO-01: Hero section with Autopitch description before interactive widgets
- DEMO-02: Cached demo pipeline function (_run_demo_pipeline with @st.cache_data)
- DEMO-03: PPTX bytes persisted in st.session_state after generation
- DEMO-04: Elapsed time and slide count stored in st.session_state
- UPLD-03: _build_template_xlsx() returns valid XLSX bytes (PK magic)

Approach: Read app.py source as text and verify required patterns using regex/string
matching. No Streamlit AppTest runtime needed for structural checks.
"""

import re
import sys
import importlib
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

APP_PATH = Path(__file__).parent.parent / "app.py"


def _source() -> str:
    """Return the full source text of app.py."""
    return APP_PATH.read_text(encoding="utf-8")


def _lines() -> list[str]:
    """Return app.py lines (0-indexed)."""
    return _source().splitlines()


def _first_line_containing(text: str, lines: list[str]) -> int:
    """Return the 0-based line index of the first line containing text, or -1."""
    for i, line in enumerate(lines):
        if text in line:
            return i
    return -1


# ---------------------------------------------------------------------------
# DEMO-01: Hero section appears BEFORE any interactive widget
# ---------------------------------------------------------------------------


class TestHeroSection:
    def test_hero_section_content(self):
        """app.py contains st.title or st.header with 'Autopitch' before any widget."""
        source = _source()
        lines = _lines()

        # Must have a title/header mentioning Autopitch
        assert re.search(r'st\.(title|header)\s*\(\s*["\'].*Autopitch', source), (
            "app.py must have st.title() or st.header() containing 'Autopitch'"
        )

        # Hero text must appear before the first interactive widget
        hero_line = -1
        for i, line in enumerate(lines):
            if re.search(r'st\.(title|header)\s*\(\s*["\'].*Autopitch', line):
                hero_line = i
                break

        widget_line = -1
        for i, line in enumerate(lines):
            if re.search(r'st\.(button|file_uploader)\s*\(', line):
                widget_line = i
                break

        assert hero_line != -1, "No hero title found in app.py"
        assert widget_line != -1, "No interactive widget found in app.py"
        assert hero_line < widget_line, (
            f"Hero section (line {hero_line+1}) must appear before first widget "
            f"(line {widget_line+1})"
        )

    def test_hero_has_descriptive_text(self):
        """app.py contains st.markdown or st.write for descriptive hero text."""
        source = _source()
        # Must have some descriptive text call (markdown or write)
        assert re.search(r"st\.(markdown|write)\s*\(", source), (
            "app.py must have st.markdown() or st.write() for hero descriptive text"
        )


# ---------------------------------------------------------------------------
# DEMO-02: Cached demo pipeline function
# ---------------------------------------------------------------------------


class TestDemoPipelineCached:
    def test_demo_pipeline_cached(self):
        """_run_demo_pipeline function exists in app.py with @st.cache_data decorator."""
        source = _source()
        lines = _lines()

        # Find @st.cache_data decorator
        cache_line = _first_line_containing("@st.cache_data", lines)
        assert cache_line != -1, "app.py must have @st.cache_data decorator"

        # Find _run_demo_pipeline function
        func_line = _first_line_containing("def _run_demo_pipeline", lines)
        assert func_line != -1, "app.py must define _run_demo_pipeline function"

        # Decorator must appear immediately before the function (within 3 lines)
        assert func_line - cache_line <= 3 and func_line > cache_line, (
            f"@st.cache_data (line {cache_line+1}) must appear just before "
            f"_run_demo_pipeline (line {func_line+1})"
        )

    def test_demo_pipeline_uses_apple_data(self):
        """_run_demo_pipeline references the bundled Apple demo file."""
        source = _source()
        assert "demo/apple_financials" in source, (
            "app.py must reference demo/apple_financials in _run_demo_pipeline"
        )

    def test_demo_pipeline_calls_run_pipeline(self):
        """_run_demo_pipeline calls run_pipeline()."""
        source = _source()
        assert re.search(r"return\s+run_pipeline\s*\(", source), (
            "app.py must call run_pipeline() inside _run_demo_pipeline"
        )


# ---------------------------------------------------------------------------
# DEMO-03: PPTX bytes stored in session_state
# ---------------------------------------------------------------------------


class TestDemoBytesInSessionState:
    def test_demo_bytes_in_session_state(self):
        """app.py references st.session_state['demo_pptx'] for storing pipeline output."""
        source = _source()
        assert re.search(r'session_state\[[\"\']demo_pptx[\"\']', source), (
            "app.py must use st.session_state['demo_pptx'] for storing pipeline output"
        )

    def test_download_button_rendered_outside_button_block(self):
        """Download button for demo is rendered based on session_state, not inside if st.button()."""
        source = _source()
        # The demo download button must reference session_state["demo_pptx"]
        # as a condition (not inside the if st.button() generate block)
        assert re.search(r'session_state\[[\"\']demo_pptx[\"\']\]\s+is\s+not\s+None', source), (
            "app.py must conditionally render demo download button using "
            "'st.session_state[\"demo_pptx\"] is not None'"
        )

    def test_download_button_on_click_ignore(self):
        """Demo download button uses on_click='ignore' parameter."""
        source = _source()
        assert re.search(r'on_click\s*=\s*["\']ignore["\']', source), (
            "app.py must use on_click='ignore' on download button(s)"
        )


# ---------------------------------------------------------------------------
# DEMO-04: Stats stored in session_state
# ---------------------------------------------------------------------------


class TestDemoStatsInSessionState:
    def test_demo_stats_in_session_state(self):
        """app.py stores demo_elapsed and demo_slides in st.session_state."""
        source = _source()
        assert re.search(r'session_state\[[\"\']demo_elapsed[\"\']', source), (
            "app.py must store demo_elapsed in st.session_state"
        )
        assert re.search(r'session_state\[[\"\']demo_slides[\"\']', source), (
            "app.py must store demo_slides in st.session_state"
        )

    def test_session_state_initialization(self):
        """app.py initializes demo_pptx, demo_elapsed, demo_slides keys before first use."""
        source = _source()
        lines = _lines()

        # All three keys must be initialized
        for key in ("demo_pptx", "demo_elapsed", "demo_slides"):
            assert key in source, f"app.py must reference session_state key '{key}'"

        # Initialization guard must appear before first widget
        init_pattern = r"not in st\.session_state"
        init_line = -1
        for i, line in enumerate(lines):
            if re.search(init_pattern, line):
                init_line = i
                break

        widget_line = -1
        for i, line in enumerate(lines):
            if re.search(r'st\.(button|file_uploader)\s*\(', line):
                widget_line = i
                break

        assert init_line != -1, (
            "app.py must initialize session state keys with 'if key not in st.session_state'"
        )
        assert widget_line != -1, "No interactive widget found in app.py"
        assert init_line < widget_line, (
            f"Session state init (line {init_line+1}) must appear before "
            f"first widget (line {widget_line+1})"
        )


# ---------------------------------------------------------------------------
# UPLD-03: _build_template_xlsx returns valid XLSX bytes
# ---------------------------------------------------------------------------


class TestTemplatexlsxBytes:
    def test_build_template_xlsx_exists(self):
        """app.py defines _build_template_xlsx function."""
        source = _source()
        assert "def _build_template_xlsx" in source, (
            "app.py must define _build_template_xlsx() function"
        )

    def test_template_xlsx_bytes(self):
        """_build_template_xlsx() returns bytes that start with PK (valid ZIP/XLSX)."""
        # Import _build_template_xlsx from app module
        # Need to mock streamlit to avoid widget rendering on import
        import unittest.mock as mock

        # Patch streamlit at module level before importing app
        st_mock = mock.MagicMock()
        st_mock.session_state = {}

        # Use a simple dict-like object for session_state
        class FakeSessionState(dict):
            def __contains__(self, key):
                return dict.__contains__(self, key)

        st_mock.session_state = FakeSessionState()

        with mock.patch.dict(sys.modules, {"streamlit": st_mock}):
            # Clear any cached app module
            if "app" in sys.modules:
                del sys.modules["app"]

            import app as app_module

            result = app_module._build_template_xlsx()

        assert isinstance(result, bytes), "_build_template_xlsx() must return bytes"
        assert result[:2] == b"PK", (
            "_build_template_xlsx() must return valid ZIP/XLSX bytes starting with 'PK'"
        )

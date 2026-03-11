"""Tests for DEPL-01: dependency splitting between runtime and dev dependencies.

Verifies that requirements.txt contains only runtime dependencies and that
requirements-dev.txt exists with dev/test tools separate from production deps.
"""

from pathlib import Path


REQUIREMENTS = Path("requirements.txt")
DEV_REQUIREMENTS = Path("requirements-dev.txt")


def _req_lines() -> list[str]:
    """Read requirements.txt and return non-empty, non-comment lines."""
    return [
        line.strip()
        for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _dev_req_lines() -> list[str]:
    """Read requirements-dev.txt and return non-empty, non-comment lines."""
    return [
        line.strip()
        for line in DEV_REQUIREMENTS.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _req_text() -> str:
    return REQUIREMENTS.read_text(encoding="utf-8")


def _dev_req_text() -> str:
    return DEV_REQUIREMENTS.read_text(encoding="utf-8")


# --- Runtime requirements.txt checks ---


def test_requirements_has_pptx():
    """requirements.txt must contain python-pptx."""
    assert "python-pptx" in _req_text(), (
        "requirements.txt is missing python-pptx — Streamlit Cloud build will fail"
    )


def test_requirements_has_matplotlib():
    """requirements.txt must contain matplotlib."""
    assert "matplotlib" in _req_text(), (
        "requirements.txt is missing matplotlib — chart generation will fail on Cloud"
    )


def test_requirements_has_openpyxl():
    """requirements.txt must contain openpyxl."""
    assert "openpyxl" in _req_text(), "requirements.txt is missing openpyxl"


def test_requirements_has_streamlit():
    """requirements.txt must contain streamlit."""
    assert "streamlit" in _req_text(), "requirements.txt is missing streamlit"


def test_requirements_has_anthropic():
    """requirements.txt must contain anthropic."""
    assert "anthropic" in _req_text(), "requirements.txt is missing anthropic"


def test_requirements_has_dotenv():
    """requirements.txt must contain python-dotenv."""
    assert "python-dotenv" in _req_text(), "requirements.txt is missing python-dotenv"


def test_requirements_no_pytest():
    """requirements.txt must NOT contain pytest — test tools go in requirements-dev.txt."""
    lines = _req_lines()
    pytest_lines = [line for line in lines if line.startswith("pytest")]
    assert not pytest_lines, (
        f"requirements.txt contains pytest (test tool in prod deps): {pytest_lines}"
    )


def test_requirements_no_pytest_cov():
    """requirements.txt must NOT contain pytest-cov."""
    lines = _req_lines()
    cov_lines = [line for line in lines if line.startswith("pytest-cov")]
    assert not cov_lines, (
        f"requirements.txt contains pytest-cov (test tool in prod deps): {cov_lines}"
    )


# --- Dev requirements-dev.txt checks ---


def test_dev_requirements_exists():
    """requirements-dev.txt must exist."""
    assert DEV_REQUIREMENTS.exists(), (
        "requirements-dev.txt not found — dev/test dependencies are not separated"
    )


def test_dev_requirements_includes_base():
    """requirements-dev.txt must include base requirements via -r requirements.txt."""
    assert "-r requirements.txt" in _dev_req_text(), (
        "requirements-dev.txt does not include base deps via '-r requirements.txt'"
    )


def test_dev_requirements_has_pytest():
    """requirements-dev.txt must contain pytest."""
    assert "pytest" in _dev_req_text(), (
        "requirements-dev.txt is missing pytest"
    )


def test_dev_requirements_has_pytest_cov():
    """requirements-dev.txt must contain pytest-cov."""
    assert "pytest-cov" in _dev_req_text(), (
        "requirements-dev.txt is missing pytest-cov"
    )

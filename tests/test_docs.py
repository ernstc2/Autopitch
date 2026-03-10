"""Tests for documentation files: README.md and .env.example.

Validates that all required sections are present in README.md and
that the .env.example file exists with the correct API key placeholder.
"""

from pathlib import Path


def test_readme_exists():
    """README.md must exist at the project root."""
    assert Path("README.md").exists(), "README.md not found at project root"


def test_readme_sections():
    """README.md must contain all required section headings."""
    readme = Path("README.md")
    assert readme.exists(), "README.md not found — cannot check sections"

    text = readme.read_text(encoding="utf-8").lower()

    required = [
        "overview",
        "quick start",
        "installation",
        "configuration",
        "api key",
        "cli",
        "streamlit",
        "excel",
        "architecture",
    ]

    missing = [section for section in required if section not in text]
    assert not missing, f"README.md is missing required sections: {missing}"


def test_env_example_exists():
    """.env.example must exist at the project root."""
    assert Path(".env.example").exists(), ".env.example not found at project root"


def test_env_example_contains_key():
    """.env.example must contain the ANTHROPIC_API_KEY placeholder."""
    env_example = Path(".env.example")
    assert env_example.exists(), ".env.example not found — cannot check contents"

    contents = env_example.read_text(encoding="utf-8")
    assert "ANTHROPIC_API_KEY" in contents, (
        ".env.example does not contain ANTHROPIC_API_KEY placeholder"
    )

"""Tests for DEPL-02: secrets management and gitignore configuration.

Verifies that .streamlit/secrets.toml is properly gitignored so it can exist
locally for development without ever being committed to the repository.
"""

import subprocess
from pathlib import Path


GITIGNORE = Path(".gitignore")
SECRETS_TOML = Path(".streamlit/secrets.toml")


def test_secrets_toml_gitignored():
    """.streamlit/secrets.toml must appear in .gitignore."""
    assert GITIGNORE.exists(), ".gitignore not found at project root"
    contents = GITIGNORE.read_text(encoding="utf-8")
    assert ".streamlit/secrets.toml" in contents, (
        ".streamlit/secrets.toml is not listed in .gitignore — "
        "secrets would be committed to the repository"
    )


def test_secrets_toml_not_tracked():
    """.streamlit/secrets.toml must NOT be tracked by git."""
    result = subprocess.run(
        ["git", "ls-files", ".streamlit/secrets.toml"],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == "", (
        ".streamlit/secrets.toml is tracked by git — "
        f"found: {result.stdout.strip()!r}. Remove it with: git rm --cached .streamlit/secrets.toml"
    )

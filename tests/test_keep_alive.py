"""Structural tests for .github/workflows/keep-alive.yml.

All checks are plain string matching — no YAML parsing required.
"""

import pathlib

WORKFLOW_PATH = pathlib.Path(".github/workflows/keep-alive.yml")


def _content() -> str:
    """Return workflow file content, or empty string if missing."""
    if WORKFLOW_PATH.exists():
        return WORKFLOW_PATH.read_text(encoding="utf-8")
    return ""


def test_workflow_file_exists():
    """keep-alive.yml must exist at .github/workflows/."""
    assert WORKFLOW_PATH.exists(), f"Workflow file not found at {WORKFLOW_PATH}"


def test_cron_schedule():
    """Workflow must include a 6-hour cron schedule."""
    assert "0 */6 * * *" in _content(), "Expected cron schedule '0 */6 * * *' not found"


def test_pings_correct_url():
    """Workflow must ping the canonical Autopitch Streamlit URL."""
    expected = "https://autopitch-54x3pzywhwscvrs9jw6yx7.streamlit.app/"
    assert expected in _content(), f"Expected URL '{expected}' not found in workflow"


def test_keepalive_workflow_step():
    """Workflow must include the gautamkrishnar/keepalive-workflow action."""
    assert "gautamkrishnar/keepalive-workflow" in _content(), (
        "Expected 'gautamkrishnar/keepalive-workflow' step not found"
    )


def test_workflow_dispatch():
    """Workflow must include workflow_dispatch trigger for manual runs."""
    assert "workflow_dispatch" in _content(), "Expected 'workflow_dispatch' trigger not found"


def test_permissions_actions_write():
    """Workflow must declare actions: write permission (required by keepalive-workflow@v2)."""
    assert "actions: write" in _content(), "Expected 'actions: write' permission not found"


def test_timeout_set():
    """Workflow must set timeout-minutes to prevent runaway jobs."""
    assert "timeout-minutes" in _content(), "Expected 'timeout-minutes' field not found"

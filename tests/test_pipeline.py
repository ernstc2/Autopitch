"""Tests for autopitch/pipeline.py — shared run_pipeline integration function.

Covers:
    INTF-01: run_pipeline(path) returns valid PPTX bytes
    INTF-02: run_pipeline(stream) returns valid PPTX bytes
    INTF-03: generate.py and app.py contain no direct pipeline function calls
"""

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from autopitch.pipeline import run_pipeline

DEMO_PATH = Path("demo/apple_financials.xlsx")


def test_run_pipeline_path():
    """INTF-01: run_pipeline with a file path returns non-empty valid PPTX bytes."""
    result = run_pipeline(DEMO_PATH)
    assert isinstance(result, bytes), "run_pipeline must return bytes"
    assert len(result) > 0, "Result must be non-empty"
    assert result[:2] == b"PK", "PPTX must start with PK zip magic bytes"


def test_run_pipeline_stream():
    """INTF-02: run_pipeline with a BinaryIO stream returns non-empty valid PPTX bytes."""
    with open(DEMO_PATH, "rb") as f:
        stream = io.BytesIO(f.read())
    result = run_pipeline(stream)
    assert isinstance(result, bytes), "run_pipeline must return bytes"
    assert len(result) > 0, "Result must be non-empty"
    assert result[:2] == b"PK", "PPTX must start with PK zip magic bytes"


def test_cli_output(tmp_path):
    """INTF-01: CLI entry point writes a valid PPTX file to disk."""
    output_file = tmp_path / "apple_financials.pptx"
    result = subprocess.run(
        [sys.executable, "generate.py", str(DEMO_PATH), "-o", str(output_file)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"generate.py exited {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert output_file.exists(), "Output .pptx file must exist"
    pptx_bytes = output_file.read_bytes()
    assert pptx_bytes[:2] == b"PK", "Output file must be a valid zip/PPTX"


def test_no_pipeline_calls_in_generate():
    """INTF-03: generate.py must not call pipeline functions directly."""
    generate_path = Path("generate.py")
    assert generate_path.exists(), "generate.py must exist at project root"
    source = generate_path.read_text(encoding="utf-8")
    forbidden = ["parse_workbook", "compute_metrics", "generate_narrative", "build_deck"]
    for name in forbidden:
        assert name not in source, (
            f"generate.py must not call {name!r} directly — use run_pipeline() instead"
        )


def test_no_pipeline_calls_in_app():
    """INTF-03: app.py must not call pipeline functions directly (skip if not yet created)."""
    app_path = Path("app.py")
    if not app_path.exists():
        pytest.skip("app.py does not exist yet — skip until Plan 04-02")
    source = app_path.read_text(encoding="utf-8")
    forbidden = ["parse_workbook", "compute_metrics", "generate_narrative", "build_deck"]
    for name in forbidden:
        assert name not in source, (
            f"app.py must not call {name!r} directly — use run_pipeline() instead"
        )

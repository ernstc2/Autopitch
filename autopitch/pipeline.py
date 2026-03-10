"""Shared pipeline: parse -> metrics -> narrative -> deck -> PPTX bytes.

Both CLI (generate.py) and Streamlit UI (app.py) call run_pipeline() exclusively.
No pipeline logic belongs in entry point files.
"""

import io
from pathlib import Path
from typing import BinaryIO, Union

from autopitch.parser import parse_workbook
from autopitch.metrics import compute_metrics
from autopitch.narrative import generate_narrative
from autopitch.deck import build_deck


def run_pipeline(source: Union[str, Path, BinaryIO]) -> bytes:
    """Full pipeline: parse -> metrics -> narrative -> deck -> PPTX bytes.

    Args:
        source: File path (str/Path) for CLI or BinaryIO stream for Streamlit.

    Returns:
        PPTX file contents as bytes. Starts with b'PK' (zip magic).

    Raises:
        ValidationError: If the workbook structure is invalid (propagated from parse_workbook).
    """
    data = parse_workbook(source)
    metrics = compute_metrics(data)
    narrative = generate_narrative(data, metrics)
    prs = build_deck(data, metrics, narrative)
    buf = io.BytesIO()
    prs.save(buf)
    return buf.getvalue()

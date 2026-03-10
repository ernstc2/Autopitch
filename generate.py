"""CLI entry point for Autopitch.

Usage:
    python generate.py demo/apple_financials.xlsx
    python generate.py demo/apple_financials.xlsx -o output/deck.pptx

load_dotenv() is called before any autopitch imports so ANTHROPIC_API_KEY is
available when the narrative module checks os.environ at call time.
"""

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from autopitch.pipeline import run_pipeline  # noqa: E402
from autopitch.models import ValidationError  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a consulting-quality PowerPoint deck from an Excel workbook."
    )
    parser.add_argument("input", help="Path to Excel workbook (.xlsx)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output .pptx path (default: <input_stem>.pptx in current directory)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else Path(input_path.stem + ".pptx")

    try:
        pptx_bytes = run_pipeline(input_path)
    except ValidationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output_path.write_bytes(pptx_bytes)
    print(f"Deck saved to: {output_path}")


if __name__ == "__main__":
    main()

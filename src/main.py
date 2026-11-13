"""Command-line entry point for the dependency visualizer."""

import argparse
from collections.abc import Sequence
import sys
from pathlib import Path

from .config import Settings, load_config


def parse_arguments(argv: Sequence[str] | None = None) -> Path:
    """Accept only the INI path; settings live in the file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config", required=True, type=Path, help="INI configuration"
    )
    return parser.parse_args(argv).config


def describe(settings: Settings) -> None:
    """Show the configured key-value pairs for stage one."""
    print(f"package: {settings.package}")
    print(f"repository: {settings.repository}")
    print(f"test_mode: {str(settings.test_mode).lower()}")
    print(f"output: {settings.output}")


def main(argv: Sequence[str] | None = None) -> int:
    """Validate settings and print them for the initial prototype."""
    try:
        settings = load_config(parse_arguments(argv))
        describe(settings)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

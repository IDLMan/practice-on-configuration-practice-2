"""Command-line entry point for the dependency visualizer."""

import argparse
from collections.abc import Sequence
import sys
from pathlib import Path

from .config import load_config
from .sources import open_source


def parse_arguments(argv: Sequence[str] | None = None) -> Path:
    """Select the INI containing all user settings."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args(argv).config


def main(argv: Sequence[str] | None = None) -> int:
    """Show direct dependencies of the selected package (stage two)."""
    try:
        settings = load_config(parse_arguments(argv))
        deps = open_source(settings).dependencies(settings.package)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"Direct dependencies of {settings.package}:")
    for name in deps:
        print(f"- {name}")
    if not deps:
        print("(none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

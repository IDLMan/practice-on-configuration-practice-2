"""Command-line entry point for the dependency visualizer."""

import argparse
from collections.abc import Sequence
import sys
from pathlib import Path

from .config import load_config
from .graph import build_graph
from .order import dependency_order
from .sources import open_source


def parse_arguments(argv: Sequence[str] | None = None) -> Path:
    """Select the required INI file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args(argv).config


def main(argv: Sequence[str] | None = None) -> int:
    """Print a stable dependency-first order for a DAG."""
    try:
        settings = load_config(parse_arguments(argv))
        graph = build_graph(open_source(settings), settings.package)
        ordered = dependency_order(graph)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"Dependency-first order for {settings.package}:")
    for index, name in enumerate(ordered, start=1):
        print(f"{index}. {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Command-line entry point for the dependency visualizer."""

import argparse
from collections.abc import Sequence
import sys
from pathlib import Path

from .config import load_config
from .graph import build_graph
from .sources import open_source


def parse_arguments(argv: Sequence[str] | None = None) -> Path:
    """Accept the required INI file path."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args(argv).config


def main(argv: Sequence[str] | None = None) -> int:
    """Print the full transitive dependency graph, including cycles."""
    try:
        settings = load_config(parse_arguments(argv))
        graph = build_graph(open_source(settings), settings.package)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"Dependency graph of {settings.package}:")
    for node, children in sorted(graph.adjacent.items()):
        print(f"{node} -> {', '.join(children) if children else '(none)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Maven dependency visualizer, practice 2 variant 21."""

import argparse
from collections.abc import Sequence
import sys
from pathlib import Path

from .config import load_config
from .graph import build_graph
from .order import dependency_order
from .sources import open_source
from .visualize import save_visualization


def parse_arguments(argv: Sequence[str] | None = None) -> Path:
    """Select the required INI configuration file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    return parser.parse_args(argv).config


def print_order(graph) -> None:
    """Print dependency-first packages, or explain any detected cycle."""
    try:
        ordered = dependency_order(graph)
    except ValueError:
        print("Loading order: unavailable (cycle in dependencies)")
        return
    print("Dependency-first order:")
    for index, name in enumerate(ordered, start=1):
        print(f"{index}. {name}")


def main(argv: Sequence[str] | None = None) -> int:
    """Load configured sources and save the complete graph visualization."""
    try:
        settings = load_config(parse_arguments(argv))
        graph = build_graph(open_source(settings), settings.package)
        plantuml_path, svg_path = save_visualization(graph, settings.output)
    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(f"Package: {settings.package}")
    print(f"Nodes: {len(graph.adjacent)}, edges: {len(graph.edges())}")
    print(f"PlantUML: {plantuml_path}")
    print(f"SVG: {svg_path}")
    print_order(graph)
    return 0


if __name__ == "__main__":
    sys.exit(main())

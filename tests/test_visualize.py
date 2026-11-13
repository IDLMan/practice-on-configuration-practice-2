"""Structural PlantUML and SVG output tests."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from xml.etree import ElementTree as ET

from src.graph import build_graph
from src.test_repo import TestRepository
from src.visualize import levels, plantuml, save_visualization, svg

ROOT = Path(__file__).resolve().parents[1]


def sample(file: str = "diamond.txt"):
    """Return the complete graph for a named fixture."""
    path = ROOT / "fixtures/graphs" / file
    return build_graph(TestRepository(str(path)), "A")


class VisualizationTests(TestCase):
    """Check that two visual formats faithfully describe the same edges."""

    def test_plantuml_syntax(self) -> None:
        """The graph produces complete PlantUML source text."""
        text = plantuml(sample())
        self.assertTrue(text.startswith("@startuml"))
        self.assertIn("N0 --> N1", text)
        self.assertTrue(text.rstrip().endswith("@enduml"))

    def test_plantuml_edges(self) -> None:
        """Every real edge yields exactly one PlantUML arrow."""
        graph = sample()
        text = plantuml(graph)
        edges = [line for line in text.splitlines() if " --> " in line]
        self.assertEqual(len(edges), len(graph.edges()))

    def test_svg_parses(self) -> None:
        """Output is valid standalone SVG XML."""
        content = svg(sample())
        root = ET.fromstring(content)
        self.assertTrue(root.tag.endswith("svg"))

    def test_svg_nodes(self) -> None:
        """SVG includes one labeled rectangle for each package."""
        graph = sample()
        root = ET.fromstring(svg(graph))
        rects = root.findall("{*}rect")
        labels = root.findall("{*}text")
        self.assertEqual(len(rects), len(graph.adjacent))
        self.assertEqual({label.text for label in labels},
                         set(graph.adjacent))

    def test_svg_arrows(self) -> None:
        """SVG arrows correspond to graph edges."""
        graph = sample()
        root = ET.fromstring(svg(graph))
        paths = root.findall("{*}path")
        self.assertEqual(len(paths), len(graph.edges()))

    def test_nested_levels(self) -> None:
        """Shortest paths determine drawing columns."""
        self.assertEqual(levels(sample())["D"], 2)

    def test_cycle_is_drawn(self) -> None:
        """Cycles are drawable despite having no loading order."""
        graph = sample("cycle.txt")
        self.assertIn("N2 --> N0", plantuml(graph))
        self.assertIn("<svg", svg(graph))

    def test_output_files(self) -> None:
        """Save SVG and textual .puml outside the project tree."""
        with TemporaryDirectory() as folder:
            destination = Path(folder) / "image.svg"
            source, picture = save_visualization(sample(), destination)
            self.assertEqual(source.suffix, ".puml")
            self.assertEqual(picture.suffix, ".svg")
            self.assertIn("@startuml", source.read_text(encoding="utf-8"))
            ET.parse(picture)

    def test_three_distinct_packages(self) -> None:
        """Demonstration INIs provide three distinct package roots."""
        from src.config import load_config
        names = [load_config(ROOT / "config" / path).package
                 for path in ("test.ini", "b.ini", "c.ini")]
        self.assertEqual(names, ["A", "B", "C"])

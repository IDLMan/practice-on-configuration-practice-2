"""Test-mode graph file validation."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from src.test_repo import TestRepository

ROOT = Path(__file__).resolve().parents[1]


class RepositoryTests(TestCase):
    """Validate synthetic A-Z dependencies."""

    def test_known_edges(self) -> None:
        """Read a complete test graph."""
        graph = TestRepository(str(ROOT / "fixtures/graphs/diamond.txt"))
        self.assertEqual(graph.dependencies("A"), ("B", "C"))
        self.assertEqual(graph.dependencies("D"), ())

    def test_missing_package(self) -> None:
        """Unknown package names are not silently accepted."""
        graph = TestRepository(str(ROOT / "fixtures/graphs/diamond.txt"))
        with self.assertRaisesRegex(ValueError, "Unknown"):
            graph.dependencies("Z")

    def test_missing_vertex_definition(self) -> None:
        """Dependencies must be declared as graph vertices."""
        self.assert_invalid("A: B\n", "Undefined")

    def test_invalid_node_spelling(self) -> None:
        """All names use only uppercase Latin letters."""
        self.assert_invalid("a: B\nB:\n", "uppercase")

    def test_duplicate_node(self) -> None:
        """Repeated definitions cannot replace earlier dependencies."""
        self.assert_invalid("A:\nA:\n", "duplicate")

    def test_invalid_separator(self) -> None:
        """Each line must have one colon."""
        self.assert_invalid("A -> B\n", "expected")

    def assert_invalid(self, text: str, pattern: str) -> None:
        """Create a temporary malformed test repository."""
        with TemporaryDirectory() as folder:
            target = Path(folder) / "bad.txt"
            target.write_text(text, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, pattern):
                TestRepository(str(target))

"""Recursive BFS graph tests, including cycles and transitive edges."""

from pathlib import Path
from unittest import TestCase

from src.graph import build_graph
from src.test_repo import TestRepository

ROOT = Path(__file__).resolve().parents[1]


def load_graph(name: str):
    """Build a graph from a local named test fixture."""
    path = ROOT / "fixtures/graphs" / name
    return build_graph(TestRepository(str(path)), "A")


class GraphTests(TestCase):
    """Check reachability, correct edges, and termination."""

    def test_bfs_diamond(self) -> None:
        """Include the shared dependency only once as a node."""
        graph = load_graph("diamond.txt")
        self.assertEqual(set(graph.adjacent), {"A", "B", "C", "D"})
        self.assertIn(("B", "D"), graph.edges())
        self.assertIn(("C", "D"), graph.edges())

    def test_cycle_retains_back_edge(self) -> None:
        """An A-B-C-A cycle must terminate and keep its edges."""
        graph = load_graph("cycle.txt")
        self.assertEqual(len(graph.adjacent), 3)
        self.assertIn(("C", "A"), graph.edges())

    def test_isolated_root(self) -> None:
        """An isolated package has an empty adjacency list."""
        graph = load_graph("isolated.txt")
        self.assertEqual(graph.adjacent, {"A": ()})

    def test_long_chain(self) -> None:
        """Recursive BFS discovers multiple transitive levels."""
        graph = load_graph("chain.txt")
        self.assertEqual(len(graph.adjacent), 5)
        self.assertEqual(graph.adjacent["E"], ())

    def test_complex_edges(self) -> None:
        """Retain edges for repeated and shared dependencies."""
        graph = load_graph("complex.txt")
        self.assertEqual(len(graph.adjacent), 8)
        self.assertIn(("G", "H"), graph.edges())
        self.assertIn(("F", "H"), graph.edges())

    def test_unknown_root(self) -> None:
        """Unknown roots report a clear error instead of an empty graph."""
        repo = TestRepository(str(ROOT / "fixtures/graphs/diamond.txt"))
        with self.assertRaisesRegex(ValueError, "Unknown"):
            build_graph(repo, "Z")

    def test_recursive_layers(self) -> None:
        """Ensure the required BFS helper calls itself recursively."""
        import ast
        import inspect
        import textwrap
        import src.graph as module

        tree = ast.parse(textwrap.dedent(inspect.getsource(module.build_graph)))
        calls = [node.func.id for node in ast.walk(tree)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)]
        self.assertGreaterEqual(calls.count("walk_layer"), 2)

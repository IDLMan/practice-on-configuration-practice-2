"""Deterministic topological dependency-order tests."""

from pathlib import Path
from unittest import TestCase

from src.graph import build_graph
from src.order import dependency_order
from src.test_repo import TestRepository

ROOT = Path(__file__).resolve().parents[1]


def order_of(file: str) -> tuple[str, ...]:
    """Compute the order of a named test graph."""
    path = ROOT / "fixtures/graphs" / file
    graph = build_graph(TestRepository(str(path)), "A")
    return dependency_order(graph)


class OrderTests(TestCase):
    """Dependencies must always precede the packages using them."""

    def test_diamond_order(self) -> None:
        """A shared dependency appears before both consumers."""
        self.assertEqual(order_of("diamond.txt"), ("D", "B", "C", "A"))

    def test_chain_order(self) -> None:
        """Topological ordering reverses a forward chain."""
        self.assertEqual(order_of("chain.txt"),
                         ("E", "D", "C", "B", "A"))

    def test_single_package(self) -> None:
        """An isolated root is the entire order."""
        self.assertEqual(order_of("isolated.txt"), ("A",))

    def test_cycle_error(self) -> None:
        """Cycles have no valid topological order."""
        with self.assertRaisesRegex(ValueError, "Cycle"):
            order_of("cycle.txt")

    def test_complex_order(self) -> None:
        """Every edge points from a later consumer to an earlier dep."""
        path = ROOT / "fixtures/graphs/complex.txt"
        graph = build_graph(TestRepository(str(path)), "A")
        ordered = dependency_order(graph)
        for parent, dep in graph.edges():
            self.assertLess(ordered.index(dep), ordered.index(parent))

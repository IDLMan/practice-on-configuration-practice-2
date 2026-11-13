"""Recursive breadth-first dependency graph construction."""

from dataclasses import dataclass

from .sources import DependencySource


@dataclass(frozen=True)
class DependencyGraph:
    """Root name and adjacency lists of all reachable packages."""

    root: str
    adjacent: dict[str, tuple[str, ...]]

    def edges(self) -> tuple[tuple[str, str], ...]:
        """List dependencies as directed edges, preserving all back edges."""
        return tuple(
            (node, dep)
            for node, children in sorted(self.adjacent.items())
            for dep in children
        )


def build_graph(source: DependencySource, root: str) -> DependencyGraph:
    """Traverse the source recursively, processing one BFS layer at a time."""
    visited = {root}
    adjacent: dict[str, tuple[str, ...]] = {}

    def walk_layer(frontier: list[str]) -> None:
        """Visit a breadth level and recurse into the next level."""
        if not frontier:
            return
        following: list[str] = []
        for node in frontier:
            children = source.dependencies(node)
            adjacent[node] = children
            for dep in children:
                if dep not in visited:
                    visited.add(dep)
                    following.append(dep)
        walk_layer(following)

    walk_layer([root])
    return DependencyGraph(root, adjacent)

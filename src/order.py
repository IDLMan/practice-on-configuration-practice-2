"""Stable topological ordering with dependencies before consumers."""

from heapq import heapify, heappop, heappush

from .graph import DependencyGraph


def build_index(adjacent: dict[str, tuple[str, ...]]
                ) -> tuple[dict[str, int], dict[str, set[str]]]:
    """Index unresolved dependencies and reverse consumer links."""
    remaining = {node: len(set(children))
                 for node, children in adjacent.items()}
    consumers: dict[str, set[str]] = {
        node: set() for node in adjacent
    }
    for parent, children in adjacent.items():
        for child in children:
            consumers[child].add(parent)
    return remaining, consumers


def dependency_order(graph: DependencyGraph) -> tuple[str, ...]:
    """Return dependency-first nodes or reject an impossible cycle."""
    remaining, consumers = build_index(graph.adjacent)
    ready = [node for node, count in remaining.items() if not count]
    heapify(ready)
    ordered: list[str] = []
    while ready:
        node = heappop(ready)
        ordered.append(node)
        for consumer in sorted(consumers[node]):
            remaining[consumer] -= 1
            if not remaining[consumer]:
                heappush(ready, consumer)
    if len(ordered) != len(remaining):
        raise ValueError("Cycle detected: dependency-first order impossible")
    return tuple(ordered)

"""Simple, strictly validated A-Z graph files for offline demonstration."""

from pathlib import Path
import re

NODE = re.compile(r"^[A-Z]+$")


class TestRepository:
    """Read a graph file containing lines such as 'A: B C'."""

    def __init__(self, path: str) -> None:
        """Load all nodes, rejecting invalid edges and duplicate rows."""
        self.graph: dict[str, tuple[str, ...]] = {}
        source = Path(path)
        try:
            content = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            raise ValueError(f"Cannot read graph: {error}") from error
        for number, line in enumerate(content.splitlines(), start=1):
            self._read_line(line, number)
        self._check_targets()

    def _read_line(self, line: str, number: int) -> None:
        """Parse one named vertex and its dependencies."""
        clean = line.partition("#")[0].strip()
        if not clean:
            return
        if clean.count(":") != 1:
            raise ValueError(f"Graph line {number}: expected 'A: B C'")
        node, values = (part.strip() for part in clean.split(":"))
        deps = tuple(values.split())
        if not NODE.fullmatch(node) or any(
            not NODE.fullmatch(dep) for dep in deps
        ):
            raise ValueError(f"Graph line {number}: only uppercase A-Z")
        if node in self.graph:
            raise ValueError(f"Graph line {number}: duplicate node {node}")
        self.graph[node] = tuple(dict.fromkeys(deps))

    def _check_targets(self) -> None:
        """Require declarations for all referenced packages."""
        for node, children in self.graph.items():
            for child in children:
                if child not in self.graph:
                    raise ValueError(f"Undefined node {child} from {node}")

    def dependencies(self, name: str) -> tuple[str, ...]:
        """Return direct dependencies of a known test package."""
        if name not in self.graph:
            raise ValueError(f"Unknown test package: {name}")
        return self.graph[name]

"""Generate PlantUML source and a stand-alone SVG from the same graph."""

from collections import deque
from pathlib import Path
from xml.etree import ElementTree as element_tree

from .graph import DependencyGraph

BOX_HEIGHT = 48
BOX_PAD = 24
COLUMN_GAP = 110
ROW_GAP = 34
BACK_EDGE_GAP = 80
MARGIN = 45
FONT_SIZE = 14
CHAR_WIDTH = 8
MIN_BOX_WIDTH = 130
SVG_NS = "http://www.w3.org/2000/svg"


def plantuml(graph: DependencyGraph) -> str:
    """Encode all graph vertices and directed edges as PlantUML text."""
    nodes = sorted(graph.adjacent)
    names = {node: f"N{index}" for index, node in enumerate(nodes)}
    lines = ["@startuml", "left to right direction",
             "skinparam shadowing false"]
    for node in nodes:
        lines.append(f'rectangle "{node}" as {names[node]}')
    for source, target in graph.edges():
        lines.append(f"{names[source]} --> {names[target]}")
    lines.append("@enduml")
    return "\n".join(lines) + "\n"


def levels(graph: DependencyGraph) -> dict[str, int]:
    """Assign each vertex its shortest breadth-first distance."""
    found = {graph.root: 0}
    queue = deque([graph.root])
    while queue:
        parent = queue.popleft()
        for dep in graph.adjacent[parent]:
            if dep not in found:
                found[dep] = found[parent] + 1
                queue.append(dep)
    return found


def positions(graph: DependencyGraph, box_width: int
              ) -> dict[str, tuple[int, int]]:
    """Place each breadth-first layer in a separate column."""
    groups: dict[int, list[str]] = {}
    for node, depth in levels(graph).items():
        groups.setdefault(depth, []).append(node)
    points: dict[str, tuple[int, int]] = {}
    for depth, names in sorted(groups.items()):
        for row, node in enumerate(sorted(names)):
            x = MARGIN + depth * (box_width + COLUMN_GAP)
            y = MARGIN + row * (BOX_HEIGHT + ROW_GAP)
            points[node] = (x, y)
    return points


def svg_element(tag: str, parent: element_tree.Element,
                **attrs: str) -> element_tree.Element:
    """Append an SVG element in the proper namespace."""
    return element_tree.SubElement(parent, f"{{{SVG_NS}}}{tag}", attrs)

def draw_edges(canvas: element_tree.Element, graph: DependencyGraph,
               points: dict[str, tuple[int, int]], width: int) -> None:
    """Draw graph arrows, routing back edges below the nodes."""
    for source, target in graph.edges():
        x1, y1 = points[source]
        x2, y2 = points[target]

        if x2 <= x1:
            start_x = x1 + width // 2
            end_x = x2 + width // 2
            bend_y = max(y1, y2) + BOX_HEIGHT + BACK_EDGE_GAP
            path = (
                f"M {start_x} {y1 + BOX_HEIGHT} "
                f"C {start_x} {bend_y}, {end_x} {bend_y}, "
                f"{end_x} {y2 + BOX_HEIGHT}"
            )
        else:
            start_x = x1 + width
            end_x = x2
            offset = 35
            path = (
                f"M {start_x} {y1 + BOX_HEIGHT // 2} "
                f"C {start_x + offset} {y1 + BOX_HEIGHT // 2}, "
                f"{end_x - offset} {y2 + BOX_HEIGHT // 2}, "
                f"{end_x} {y2 + BOX_HEIGHT // 2}"
            )

        arrow = svg_element("path", canvas, d=path, fill="none",
                            stroke="#64748b", **{"stroke-width": "2"})
        arrow.set("marker-end", "url(#arrow)")

def draw_nodes(canvas: element_tree.Element,
               points: dict[str, tuple[int, int]], width: int) -> None:
    """Draw accessible labeled rectangles for every package."""
    for node, (x, y) in sorted(points.items()):
        svg_element("rect", canvas, x=str(x), y=str(y),
                    width=str(width), height=str(BOX_HEIGHT),
                    rx="9", fill="#eff6ff", stroke="#2563eb")
        label = svg_element("text", canvas, x=str(x + BOX_PAD),
                            y=str(y + BOX_HEIGHT // 2 + 5),
                            fill="#0f172a", **{"font-size": str(FONT_SIZE)})
        label.text = node


def svg(graph: DependencyGraph) -> str:
    """Render a self-contained SVG graph without external dependencies."""
    box_width = max(MIN_BOX_WIDTH,
                    max(len(node) for node in graph.adjacent)
                    * CHAR_WIDTH + BOX_PAD * 2)
    points = positions(graph, box_width)
    width = max(x for x, _ in points.values()) + box_width + MARGIN
    height = (max(y for _, y in points.values()) + BOX_HEIGHT
          + BACK_EDGE_GAP + MARGIN)
    element_tree.register_namespace("", SVG_NS)
    canvas = element_tree.Element(f"{{{SVG_NS}}}svg", {
        "width": str(width), "height": str(height),
        "viewBox": f"0 0 {width} {height}",
    })
    title = svg_element("title", canvas)
    title.text = f"Dependencies of {graph.root}"
    defs = svg_element("defs", canvas)
    marker = svg_element("marker", defs, id="arrow", markerWidth="10",
                         markerHeight="10", refX="9", refY="3",
                         orient="auto", markerUnits="strokeWidth")
    svg_element("path", marker, d="M0,0 L0,6 L9,3 z", fill="#64748b")
    draw_edges(canvas, graph, points, box_width)
    draw_nodes(canvas, points, box_width)
    return element_tree.tostring(
        canvas,
        encoding="unicode",
        xml_declaration=True,
    )


def save_visualization(graph: DependencyGraph,
                       output: Path) -> tuple[Path, Path]:
    """Write a PlantUML source and corresponding SVG to output paths."""
    source = output.with_suffix(".puml")
    output.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(plantuml(graph), encoding="utf-8")
    output.write_text(svg(graph), encoding="utf-8")
    return source, output

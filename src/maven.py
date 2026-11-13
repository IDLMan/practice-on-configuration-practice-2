"""Fetch Maven POMs over HTTP and parse dependencies without Maven or pip."""

import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

MISSING_VAR = re.compile(r"\$\{([^}]+)\}")
IGNORED_SCOPES = {"test", "provided", "system", "import"}
POM_MAX_BYTES = 2_000_000
REQUEST_TIMEOUT = 12


def child(element: ET.Element | None, name: str) -> ET.Element | None:
    """Find a direct XML child independently of the POM namespace."""
    if element is None:
        return None
    return element.find(f"{{*}}{name}")


def value(element: ET.Element | None, name: str) -> str:
    """Read text from one XML child or return an empty value."""
    node = child(element, name)
    return "" if node is None else (node.text or "").strip()


def properties(root: ET.Element, package: str) -> dict[str, str]:
    """Collect common project, parent and local version properties."""
    group, artifact, version = package.split(":")
    parent = child(root, "parent")
    values = {
        "project.groupId": group,
        "pom.groupId": group,
        "project.artifactId": artifact,
        "project.version": version,
        "pom.version": version,
        "parent.version": value(parent, "version"),
        "project.parent.version": value(parent, "version"),
    }
    entry = child(root, "properties")
    if entry is not None:
        for item in entry:
            key = item.tag.split("}")[-1]
            values[key] = (item.text or "").strip()
    return values


def resolve(text: str, values: dict[str, str]) -> str:
    """Expand supported ${property} expressions with a finite limit."""
    for _ in range(10):
        expanded = MISSING_VAR.sub(
            lambda match: values.get(match.group(1), match.group(0)),
            text,
        )
        if expanded == text:
            break
        text = expanded
    if MISSING_VAR.search(text):
        raise ValueError(f"Unresolved Maven property: {text}")
    return text


def managed_versions(root: ET.Element, vars: dict[str, str]
                     ) -> dict[tuple[str, str], str]:
    """Read versions declared in this POM's dependencyManagement."""
    block = child(child(root, "dependencyManagement"), "dependencies")
    versions: dict[tuple[str, str], str] = {}
    if block is None:
        return versions
    for dep in block.findall("{*}dependency"):
        group = resolve(value(dep, "groupId"), vars)
        artifact = resolve(value(dep, "artifactId"), vars)
        version = resolve(value(dep, "version"), vars)
        versions[group, artifact] = version
    return versions


def parse_pom(xml: bytes, package: str,
              inherited_vars: dict[str, str] | None = None,
              inherited_managed: dict[tuple[str, str], str] | None = None
              ) -> tuple[str, ...]:
    """Parse a POM's direct runtime dependencies and declared versions."""
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as error:
        raise ValueError(f"Invalid Maven POM XML: {error}") from error
    vars = {**(inherited_vars or {}), **properties(root, package)}
    managed = {**(inherited_managed or {}),
               **managed_versions(root, vars)}
    block = child(root, "dependencies")
    if block is None:
        return ()
    result: list[str] = []
    for dependency in block.findall("{*}dependency"):
        coord = parse_dependency(dependency, vars, managed)
        if coord and coord not in result:
            result.append(coord)
    return tuple(result)


def parse_dependency(dep: ET.Element, vars: dict[str, str],
                     managed: dict[tuple[str, str], str]) -> str:
    """Return a complete package coordinate or skip an inactive edge."""
    if value(dep, "scope") in IGNORED_SCOPES:
        return ""
    if value(dep, "optional").lower() == "true":
        return ""
    if value(dep, "type") not in ("", "jar"):
        return ""
    group = resolve(value(dep, "groupId"), vars)
    artifact = resolve(value(dep, "artifactId"), vars)
    raw = value(dep, "version") or managed.get((group, artifact), "")
    version = resolve(raw, vars)
    if not all((group, artifact, version)):
        raise ValueError(f"Missing dependency version: {group}:{artifact}")
    return f"{group}:{artifact}:{version}"


class MavenRepository:
    """Fetch direct dependencies from a repository's XML POM metadata."""

    def __init__(self, url: str) -> None:
        """Record repository URL and initialize a per-run read cache."""
        self.base_url = url.rstrip("/")
        self.cache: dict[str, tuple[str, ...]] = {}
        self.pom_cache: dict[str, bytes] = {}

    def dependencies(self, name: str) -> tuple[str, ...]:
        """Fetch POM bytes and resolve direct runtime dependencies."""
        if name not in self.cache:
            xml = self._download(name)
            parent_vars, parent_managed = self._parent_context(xml, {name})
            self.cache[name] = parse_pom(
                xml, name, parent_vars, parent_managed
            )
        return self.cache[name]

    def _parent_context(self, xml: bytes, seen: set[str]
                        ) -> tuple[dict[str, str],
                                   dict[tuple[str, str], str]]:
        """Resolve dependencyManagement through parent POMs."""
        try:
            root = ET.fromstring(xml)
        except ET.ParseError as error:
            raise ValueError(f"Invalid Maven POM XML: {error}") from error
        parent = child(root, "parent")
        if parent is None:
            return {}, {}
        parts = tuple(value(parent, part) for part in (
            "groupId", "artifactId", "version"
        ))
        if not all(parts):
            raise ValueError("Incomplete Maven parent coordinates")
        name = ":".join(parts)
        if name in seen:
            raise ValueError(f"Cycle in Maven POM parent chain: {name}")
        parent_xml = self._download(name)
        vars, managed = self._parent_context(parent_xml, seen | {name})
        vars = {**vars, **properties(ET.fromstring(parent_xml), name)}
        managed = {**managed,
                   **managed_versions(ET.fromstring(parent_xml), vars)}
        return vars, managed

    def _download(self, name: str) -> bytes:
        """Download a POM from a Maven2 repository URL."""
        if name in self.pom_cache:
            return self.pom_cache[name]
        group, artifact, version = name.split(":")
        group_path = "/".join(quote(x, safe="") for x in group.split("."))
        artifact = quote(artifact, safe="")
        version = quote(version, safe="")
        path = f"{group_path}/{artifact}/{version}/{artifact}-{version}.pom"
        request = Request(f"{self.base_url}/{path}")
        try:
            with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
                xml = response.read(POM_MAX_BYTES + 1)
        except (HTTPError, URLError, TimeoutError, OSError) as error:
            raise ValueError(f"Cannot fetch Maven POM for {name}: {error}")
        if len(xml) > POM_MAX_BYTES:
            raise ValueError(f"Maven POM too large: {name}")
        self.pom_cache[name] = xml
        return xml

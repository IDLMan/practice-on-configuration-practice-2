"""Strict INI-only user configuration for dependency visualization."""

import configparser
from dataclasses import dataclass
from pathlib import Path
import re
from urllib.parse import urlsplit

PACKAGE_PART = re.compile(r"^[A-Za-z0-9_.-]+$")
TEST_PACKAGE = re.compile(r"^[A-Z]+$")
COORDINATE_FIELDS = 3


@dataclass(frozen=True)
class Settings:
    """All four configurable values from variant 21."""

    package: str
    repository: str
    test_mode: bool
    output: Path


def read_ini(path: Path) -> dict[str, str]:
    """Read an INI file without accepting duplicate keys."""
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding="utf-8") as stream:
            parser.read_file(stream)
    except (OSError, UnicodeError, configparser.Error) as error:
        raise ValueError(f"Cannot read INI: {error}") from error
    if not parser.has_section("settings"):
        raise ValueError("INI must contain [settings]")
    required = {"package", "repository", "test_mode", "output"}
    missing = required - set(parser["settings"])
    if missing:
        raise ValueError(f"Missing INI keys: {', '.join(sorted(missing))}")
    return dict(parser["settings"])


def validate_package(package: str, test_mode: bool) -> None:
    """Validate uppercase test nodes or Maven coordinates."""
    if test_mode:
        if not TEST_PACKAGE.fullmatch(package):
            raise ValueError("Test package must use uppercase A-Z")
        return
    parts = package.split(":")
    if len(parts) != COORDINATE_FIELDS or any(not PACKAGE_PART.fullmatch(p)
                              for p in parts):
        raise ValueError("Maven package must be group:artifact:version")
    if any(part in (".", "..") for part in parts):
        raise ValueError("Package coordinates must not contain dot paths")


def validate_repository(value: str, test_mode: bool) -> None:
    """Check that the selected data source can be addressed."""
    if test_mode:
        if not Path(value).is_file():
            raise ValueError(f"Test graph file not found: {value}")
        return
    parsed = urlsplit(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise ValueError("Maven repository requires an http(s) URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Maven repository URL contains unsupported parts")


def load_config(path: Path) -> Settings:
    """Load and validate all settings, resolving paths against the INI."""
    ini = path.resolve()
    raw = read_ini(ini)
    mode = raw["test_mode"].strip().lower()
    if mode not in ("true", "false"):
        raise ValueError("test_mode must be true or false")
    test_mode = mode == "true"
    package = raw["package"].strip()
    repository = raw["repository"].strip()
    output = raw["output"].strip()
    validate_package(package, test_mode)
    if test_mode:
        repository = str((ini.parent / repository).resolve())
    validate_repository(repository, test_mode)
    if not output or Path(output).suffix.lower() != ".svg":
        raise ValueError("output must name an .svg file")
    destination = (ini.parent / output).resolve()
    return Settings(package, repository, test_mode, destination)

"""INI configuration tests, including invalid user parameters."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from src.config import load_config, validate_package

ROOT = Path(__file__).resolve().parents[1]


class ConfigTests(TestCase):
    """Validate INI parsing and error messages."""

    def test_sample_config(self) -> None:
        """The shipped offline configuration must be usable."""
        settings = load_config(ROOT / "config/test.ini")
        self.assertEqual(settings.package, "A")
        self.assertTrue(settings.test_mode)
        self.assertEqual(Path(settings.repository).name, "diamond.txt")

    def test_remote_config(self) -> None:
        """Accept an HTTPS Maven source with coordinates."""
        settings = load_config(ROOT / "config/remote.ini")
        self.assertFalse(settings.test_mode)
        self.assertEqual(settings.package, "org.slf4j:slf4j-simple:2.0.13")

    def test_missing_ini(self) -> None:
        """Missing configuration files must fail clearly."""
        with self.assertRaisesRegex(ValueError, "Cannot read INI"):
            load_config(ROOT / "config/missing.ini")

    def test_bad_package(self) -> None:
        """Test nodes cannot contain lowercase letters."""
        with self.assertRaisesRegex(ValueError, "uppercase"):
            validate_package("bad", True)

    def test_maven_coordinates(self) -> None:
        """Maven coordinates need all three parts."""
        with self.assertRaisesRegex(ValueError, "group:artifact:version"):
            validate_package("org.demo:lib", False)

    def test_missing_section(self) -> None:
        """The INI section is mandatory."""
        self.assert_invalid("[wrong]\npackage = A\n", "settings")

    def test_missing_key(self) -> None:
        """Every required parameter must be present."""
        self.assert_invalid("[settings]\npackage = A\n", "Missing")

    def test_bad_bool(self) -> None:
        """Unknown booleans must be rejected."""
        self.assert_invalid(self.good_ini().replace("true", "yes"),
                            "test_mode")

    def test_missing_graph(self) -> None:
        """Reject a nonexistent test repository file."""
        self.assert_invalid(self.good_ini().replace("diamond.txt", "no.txt"),
                            "not found")

    def test_bad_extension(self) -> None:
        """The output format is always SVG."""
        self.assert_invalid(self.good_ini().replace("graph.svg", "graph.png"),
                            "svg")

    def test_bad_url(self) -> None:
        """Maven source must use http or https."""
        ini = self.good_ini().replace("test_mode = true", "test_mode = false")
        ini = ini.replace("package = A", "package = org.demo:lib:1.0")
        self.assert_invalid(ini.replace("diamond.txt", "not-a-url"),
                            "http")

    def test_duplicate_key(self) -> None:
        """Reject malformed INI with duplicate keys."""
        self.assert_invalid(self.good_ini() + "\npackage = B\n",
                            "Cannot read INI")

    def assert_invalid(self, content: str, pattern: str) -> None:
        """Load a temporary INI and expect a configuration error."""
        with TemporaryDirectory() as folder:
            ini = Path(folder) / "settings.ini"
            ini.write_text(content, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, pattern):
                load_config(ini)

    @staticmethod
    def good_ini() -> str:
        """Return portable INI text with a known example graph."""
        graph = ROOT / "fixtures/graphs/diamond.txt"
        return ("[settings]\npackage = A\n"
                f"repository = {graph}\n"
                "test_mode = true\noutput = graph.svg\n")

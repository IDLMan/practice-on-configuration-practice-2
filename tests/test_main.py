"""Final application behavior tests."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from src.main import main

ROOT = Path(__file__).resolve().parents[1]


class MainTests(TestCase):
    """Check user output and saved image files."""

    def test_writes_svg_and_puml(self) -> None:
        """CLI saves two formats with an independent temporary INI."""
        with TemporaryDirectory() as folder:
            ini = Path(folder) / "test.ini"
            graph = ROOT / "fixtures/graphs/diamond.txt"
            ini.write_text(
                "[settings]\npackage = A\n"
                f"repository = {graph}\ntest_mode = true\n"
                "output = image.svg\n", encoding="utf-8"
            )
            buffer = StringIO()
            with redirect_stdout(buffer):
                code = main(["--config", str(ini)])
            self.assertEqual(code, 0)
            self.assertTrue((Path(folder) / "image.svg").is_file())
            self.assertTrue((Path(folder) / "image.puml").is_file())
            self.assertIn("Dependency-first order", buffer.getvalue())

    def test_cycle_saves_svg(self) -> None:
        """The image is still useful for cyclic dependencies."""
        with TemporaryDirectory() as folder:
            source = ROOT / "fixtures/graphs/cycle.txt"
            ini = Path(folder) / "cycle.ini"
            ini.write_text(
                "[settings]\npackage = A\n"
                f"repository = {source}\ntest_mode = true\n"
                "output = image.svg\n", encoding="utf-8"
            )
            buffer = StringIO()
            with redirect_stdout(buffer):
                code = main(["--config", str(ini)])
            self.assertEqual(code, 0)
            self.assertIn("unavailable", buffer.getvalue())

    def test_bad_config_returns_error(self) -> None:
        """Invalid configuration yields nonzero exit code."""
        buffer = StringIO()
        with redirect_stderr(buffer):
            code = main(["--config", "missing.ini"])
        self.assertEqual(code, 2)
        self.assertIn("Error:", buffer.getvalue())

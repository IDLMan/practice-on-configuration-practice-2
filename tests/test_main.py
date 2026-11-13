"""Stage three CLI tests."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase

from src.main import main

ROOT = Path(__file__).resolve().parents[1]


class MainTests(TestCase):
    """Check the full graph report and user errors."""

    def test_prints_transitive_dependencies(self) -> None:
        """The output includes the second-level edge B-D."""
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = main(["--config", str(ROOT / "config/test.ini")])
        self.assertEqual(code, 0)
        self.assertIn("B -> D", buffer.getvalue())

    def test_prints_cycle(self) -> None:
        """The cycle fixture must display its closing edge."""
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = main(["--config", str(ROOT / "config/cycle.ini")])
        self.assertEqual(code, 0)
        self.assertIn("C -> A", buffer.getvalue())

    def test_bad_config_returns_error(self) -> None:
        """Error status must remain stable across stages."""
        buffer = StringIO()
        with redirect_stderr(buffer):
            code = main(["--config", "missing.ini"])
        self.assertEqual(code, 2)
        self.assertIn("Error:", buffer.getvalue())

"""Stage four user interface tests."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase

from src.main import main

ROOT = Path(__file__).resolve().parents[1]


class MainTests(TestCase):
    """Check the order printer and error propagation."""

    def test_prints_dependency_first_order(self) -> None:
        """Diamond dependencies appear before their consumers."""
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = main(["--config", str(ROOT / "config/test.ini")])
        self.assertEqual(code, 0)
        self.assertIn("1. D", buffer.getvalue())
        self.assertIn("4. A", buffer.getvalue())

    def test_cycle_is_reported(self) -> None:
        """A cyclic test graph cannot have a loading order."""
        buffer = StringIO()
        with redirect_stderr(buffer):
            code = main(["--config", str(ROOT / "config/cycle.ini")])
        self.assertEqual(code, 2)
        self.assertIn("Cycle", buffer.getvalue())

    def test_bad_config_returns_error(self) -> None:
        """Invalid settings return a failure result."""
        buffer = StringIO()
        with redirect_stderr(buffer):
            code = main(["--config", "no.ini"])
        self.assertEqual(code, 2)
        self.assertIn("Error:", buffer.getvalue())

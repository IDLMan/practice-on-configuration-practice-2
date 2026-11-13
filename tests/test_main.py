"""Stage two command-line tests."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase

from src.main import main

ROOT = Path(__file__).resolve().parents[1]


class MainTests(TestCase):
    """Check user-visible direct dependency reports."""

    def test_prints_direct_dependencies(self) -> None:
        """The application displays only the first layer."""
        buffer = StringIO()
        with redirect_stdout(buffer):
            result = main(["--config", str(ROOT / "config/test.ini")])
        self.assertEqual(result, 0)
        self.assertIn("- B", buffer.getvalue())
        self.assertIn("- C", buffer.getvalue())
        self.assertNotIn("- D", buffer.getvalue())

    def test_bad_config_returns_error(self) -> None:
        """Return a nonzero code for configuration errors."""
        buffer = StringIO()
        with redirect_stderr(buffer):
            result = main(["--config", "does-not-exist.ini"])
        self.assertEqual(result, 2)
        self.assertIn("Error:", buffer.getvalue())

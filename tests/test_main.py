"""Stage one command-line tests."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest import TestCase

from src.main import main

ROOT = Path(__file__).resolve().parents[1]


class MainTests(TestCase):
    """Check observable console behavior."""

    def test_prints_all_settings(self) -> None:
        """Stage one prints four key-value settings."""
        buffer = StringIO()
        with redirect_stdout(buffer):
            result = main(["--config", str(ROOT / "config/test.ini")])
        self.assertEqual(result, 0)
        self.assertIn("package: A", buffer.getvalue())
        self.assertIn("test_mode: true", buffer.getvalue())
        self.assertIn("output:", buffer.getvalue())
        self.assertIn("repository:", buffer.getvalue())

    def test_bad_config_returns_error(self) -> None:
        """User errors produce a nonzero exit result."""
        buffer = StringIO()
        with redirect_stderr(buffer):
            result = main(["--config", "does-not-exist.ini"])
        self.assertEqual(result, 2)
        self.assertIn("Error:", buffer.getvalue())

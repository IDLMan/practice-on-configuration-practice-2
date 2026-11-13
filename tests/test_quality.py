"""Automated checks mirroring the repository review table for Python."""

import ast
from pathlib import Path
import re
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
MAX_LINES = 1_000
MAX_COLUMN = 80
MAX_FUNCTION = 40
MAX_PARAMETERS = 7
MAX_COMPLEXITY = 10
ALLOWED_NUMBERS = {0, 1}
NAME = re.compile(r"^[a-z_][a-z0-9_]*$")


def python_files() -> tuple[Path, ...]:
    """Return project Python source and tests."""
    return tuple(sorted((ROOT / "src").rglob("*.py"))) + tuple(
        sorted((ROOT / "tests").rglob("*.py"))
    )


def complexity(node: ast.FunctionDef) -> int:
    """Estimate cyclomatic complexity using AST decisions."""
    score = 1
    for part in ast.walk(node):
        if isinstance(part, (ast.If, ast.For, ast.While,
                             ast.ExceptHandler, ast.IfExp)):
            score += 1
        if isinstance(part, ast.BoolOp):
            score += len(part.values) - 1
        if isinstance(part, ast.comprehension):
            score += 1 + len(part.ifs)
    return score


class QualityTests(TestCase):
    """Prevent recurrence of the teacher's format/style violations."""

    def test_structure(self) -> None:
        """Essential entry points and metadata must exist."""
        for path in ("README.md", ".gitignore", "src", "tests",
                     "run.bat", "run.sh"):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists())

    def test_lines(self) -> None:
        """Python source must obey both line-length and file limits."""
        for path in python_files():
            lines = path.read_text(encoding="utf-8").splitlines()
            with self.subTest(path=path):
                self.assertLessEqual(len(lines), MAX_LINES)
                self.assertTrue(all(len(line) <= MAX_COLUMN
                                    for line in lines))

    def test_function_names_and_size(self) -> None:
        """Function names, argument counts and sizes follow PEP 8."""
        for path in python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                with self.subTest(path=path.name, function=node.name):
                    self.assertRegex(node.name, NAME)
                    self.assertLessEqual(node.end_lineno - node.lineno + 1,
                                         MAX_FUNCTION)
                    self.assertLessEqual(len(node.args.args), MAX_PARAMETERS)

    def test_complexity_and_docstrings(self) -> None:
        """Functions need docstrings and manageable complexity."""
        for path in python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    with self.subTest(path=path.name, name=node.name):
                        self.assertIsNotNone(ast.get_docstring(node))
                        self.assertLessEqual(complexity(node), MAX_COMPLEXITY)

    def test_magic_comparison_numbers(self) -> None:
        """No unexplained numeric constants should occur in comparisons."""
        for path in python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Compare):
                    items = [node.left, *node.comparators]
                    for item in items:
                        if isinstance(item, ast.Constant) and isinstance(
                            item.value, (int, float)
                        ):
                            self.assertIn(item.value, ALLOWED_NUMBERS)


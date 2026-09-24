"""Tests that enforce the project-level Python docstring standard."""

import ast
from pathlib import Path

ROOTS_TO_CHECK = (Path("src"), Path("tests"))


def _iter_python_files() -> list[Path]:
    """Return Python source files that are subject to the documentation policy."""

    return sorted(
        path
        for root in ROOTS_TO_CHECK
        for path in root.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def test_functions_and_methods_have_docstrings() -> None:
    """Fail when a defined Python function or method lacks a useful docstring."""

    missing: list[str] = []

    for path in _iter_python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if ast.get_docstring(node) is None:
                    missing.append(f"{path}:{node.lineno} {node.name}")

    assert not missing, "Missing docstrings:\n" + "\n".join(missing)

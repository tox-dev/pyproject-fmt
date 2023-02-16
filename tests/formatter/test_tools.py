from __future__ import annotations

from pyproject_fmt.formatter.tools import fmt_tools
from tests import Fmt


def test_tools_ordering(fmt: Fmt) -> None:
    content = """
    [tool.coverage]
    a = 0
    [tool.pytest]
    a = 0
    [tool.black]
    a = 0
    [tool.isort]
    a = 0
    [tool.flake8]
    [tool.hatch]
    a = 0
    [tool.setuptools_scm]
    a = 0
    [tool.setuptools]
    a.b = 0

    """
    expected = """
    [tool.setuptools]
    a.b = 0

    [tool.setuptools_scm]
    a = 0

    [tool.hatch]
    a = 0

    [tool.black]
    a = 0

    [tool.isort]
    a = 0

    [tool.flake8]

    [tool.pytest]
    a = 0

    [tool.coverage]
    a = 0
        """
    fmt(fmt_tools, content, expected)


def test_sub_table_newline(fmt: Fmt) -> None:
    content = """
    [tool.mypy]
    a = 0

    [[tool.mypy.overrides]]
    a = 1
    [tool.something-else]
    b = 0
    """
    expected = """
    [tool.mypy]
    a = 0

    [[tool.mypy.overrides]]
    a = 1

    [tool.something-else]
    b = 0
    """
    fmt(fmt_tools, content, expected)


def test_sub_table_no_op(fmt: Fmt) -> None:
    content = """
    [tool.mypy]
    a = 0

    [[tool.mypy.overrides]]
    a = 1

    [tool.something-else]
    b = 0
    """
    fmt(fmt_tools, content, content)

from __future__ import annotations

from typing import TYPE_CHECKING

from pyproject_fmt.formatter.tools import fmt_tools

if TYPE_CHECKING:
    from tests import Fmt


def test_tools_ordering(fmt: Fmt) -> None:
    content = """
    [tool.poetry]
    name = "a"
    [tool.coverage]
    a = 0
    [tool.poetry.scripts]
    version = "1"
    [tool.scikit-build]
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
    [tool.docformatter]
    c = 0
    [tool.autopep8]
    a = 0
    [tool.distutils]
    a = 0
    [tool.codespell]
    [tool.meson-python]
    a = 0
    [tool.cibuildwheel]
    a = 0
    [tool.pylint]
    [tool.repo-review]
    a = 0
    [tool.flit]
    """
    expected = """
    [tool.poetry]
    name = "a"
    [tool.poetry.scripts]
    version = "1"
    [tool.setuptools]
    a.b = 0

    [tool.distutils]
    a = 0

    [tool.setuptools_scm]
    a = 0

    [tool.hatch]
    a = 0

    [tool.flit]

    [tool.scikit-build]
    a = 0

    [tool.meson-python]
    a = 0

    [tool.cibuildwheel]
    a = 0

    [tool.autopep8]
    a = 0

    [tool.black]
    a = 0

    [tool.isort]
    a = 0

    [tool.flake8]

    [tool.pylint]

    [tool.repo-review]
    a = 0

    [tool.codespell]

    [tool.docformatter]
    c = 0

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

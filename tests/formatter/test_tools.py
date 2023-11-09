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
    [tool.bumpversion]
    [tool.check-manifest]
    [tool.check-sdist]
    [tool.check-wheel-contents]
    [tool.doit]
    [tool.flit]
    [tool.jupyter-releaser]
    [tool.maturin]
    [tool.mypy]
    [tool.nbqa]
    [tool.pdm]
    [tool.py-build-cmake]
    [tool.pycln]
    [tool.pydoclint]
    [tool.pyright]
    [tool.pytest-enabler]
    [tool.pytest_env]
    [tool.sphinx-theme-builder]
    [tool.spin]
    [tool.tbump]
    [tool.tomlsort]
    [tool.towncrier]
    [tool.tox]
    [tool.vendoring]
    [tool.whey]
    """
    expected = """
    [tool.poetry]
    name = "a"
    [tool.poetry.scripts]
    version = "1"
    [tool.pdm]

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

    [tool.maturin]

    [tool.whey]

    [tool.py-build-cmake]

    [tool.sphinx-theme-builder]

    [tool.cibuildwheel]
    a = 0

    [tool.autopep8]
    a = 0

    [tool.black]
    a = 0

    [tool.isort]
    a = 0

    [tool.flake8]

    [tool.pycln]

    [tool.nbqa]

    [tool.pylint]

    [tool.repo-review]
    a = 0

    [tool.codespell]

    [tool.docformatter]
    c = 0

    [tool.pydoclint]

    [tool.tomlsort]

    [tool.check-manifest]

    [tool.check-sdist]

    [tool.check-wheel-contents]

    [tool.pytest]
    a = 0

    [tool.pytest_env]

    [tool.pytest-enabler]

    [tool.coverage]
    a = 0

    [tool.doit]

    [tool.spin]

    [tool.tox]

    [tool.bumpversion]

    [tool.jupyter-releaser]

    [tool.tbump]

    [tool.towncrier]

    [tool.vendoring]

    [tool.mypy]

    [tool.pyright]
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

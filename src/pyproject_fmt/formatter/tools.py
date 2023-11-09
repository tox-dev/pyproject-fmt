"""Format custom tools."""
from __future__ import annotations

from typing import TYPE_CHECKING, cast

from tomlkit.items import Table

from .util import ensure_newline_at_end, order_keys

if TYPE_CHECKING:
    from tomlkit import TOMLDocument

    from .config import Config


def fmt_tools(parsed: TOMLDocument, conf: Config) -> None:  # noqa: ARG001
    """
    Format the custom tools.

    :param parsed: the raw parsed document
    :param conf: configuration
    """
    tools: Table | None = parsed.get("tool")
    if tools is None:
        return
    for tool in tools:
        table = tools[tool]
        ensure_newline_at_end(cast(Table, table))
    order = [
        # Build backends
        "poetry",
        "pdm",
        "setuptools",
        "distutils",
        "setuptools_scm",
        "hatch",
        "flit",
        "scikit-build",
        "meson-python",
        "maturin",
        "whey",
        "py-build-cmake",
        "sphinx-theme-builder",
        # Builders
        "cibuildwheel",
        # Formatters and linters
        "autopep8",
        "black",
        "ruff",
        "isort",
        "flake8",
        "pycln",
        "nbqa",
        "pylint",
        "repo-review",
        "codespell",
        "docformatter",
        "pydoclint",
        "tomlsort",
        "check-manifest",
        "check-sdist",
        "check-wheel-contents",
        # Testing
        "pytest",
        "pytest_env",
        "pytest-enabler",
        "coverage",
        # Runners
        "doit",
        "spin",
        "tox",
        # Releasers/bumpers
        "bumpversion",
        "jupyter-releaser",
        "tbump",
        "towncrier",
        "vendoring",
        # Type checking
        "mypy",
        "pyright",
    ]
    order_keys(tools, to_pin=order)


__all__ = [
    "fmt_tools",
]

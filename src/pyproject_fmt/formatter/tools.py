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
        "poetry",
        "setuptools",
        "setuptools_scm",
        "hatch",
        "autopep8",
        "black",
        "ruff",
        "isort",
        "flake8",
        "pytest",
        "coverage",
        "mypy",
    ]
    order_keys(tools, to_pin=order)


__all__ = [
    "fmt_tools",
]

from __future__ import annotations

from typing import cast

from tomlkit import TOMLDocument
from tomlkit.items import Table

from .config import Config
from .util import ensure_newline_at_end, order_keys


def fmt_tools(parsed: TOMLDocument, conf: Config) -> None:  # noqa: U100
    tools: Table | None = parsed.get("tool")
    if tools is None:
        return None
    for tool in tools:
        table = tools[tool]
        ensure_newline_at_end(cast(Table, table))
    order = [
        "setuptools",
        "setuptools_scm",
        "hatch",
        "black",
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

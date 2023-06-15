"""Logic related to how to format."""
from __future__ import annotations

from typing import TYPE_CHECKING

from tomlkit import parse

from .build_system import fmt_build_system
from .project import fmt_project
from .tools import fmt_tools

if TYPE_CHECKING:
    from tomlkit.toml_document import TOMLDocument

    from .config import Config


def _perform(parsed: TOMLDocument, conf: Config) -> None:
    fmt_build_system(parsed, conf)
    fmt_project(parsed, conf)
    fmt_tools(parsed, conf)


def format_pyproject(conf: Config) -> str:
    """
    Format a ``pyproject.toml`` text.

    :param conf: the formatting configuration
    :return: the formatted text
    """
    parsed: TOMLDocument = parse(conf.toml)
    _perform(parsed, conf)
    result = parsed.as_string().rstrip("\n")
    return f"{result}\n"


__all__ = [
    "format_pyproject",
]

from __future__ import annotations

from tomlkit import parse
from tomlkit.toml_document import TOMLDocument

from ..cli import PyProjectFmtNamespace
from .build_system import fmt_build_system
from .project import fmt_project


def _perform(parsed: TOMLDocument, opts: PyProjectFmtNamespace) -> None:
    fmt_build_system(parsed, opts)
    fmt_project(parsed, opts)


def format_pyproject(text: str, opts: PyProjectFmtNamespace) -> str:
    r"""
    Format a string with the equivalent content of a ``pyproject.toml`` file.

    Usage:

    >>> from pyproject_fmt import PyProjectFmtNamespace, format_pyproject
    >>> text = '[project]\nname = "myproj"\nversion = "0.1.1"'
    >>> opts = PyProjectFmtNamespace(indent=2)
    >>> format_pyproject(text, opts)
    '[project]\nname = "myproj"\nversion = "0.1.1"\n'

    :param text: the contents of the TOML file as an UTF-8 string
    :param opts: object with the formatting options
    :return: the formatted TOML string that can be saved to a ``pyproject.toml`` file.
    """

    parsed: TOMLDocument = parse(text)
    _perform(parsed, opts)
    result = parsed.as_string().rstrip("\n")
    return f"{result}\n"


__all__ = [
    "format_pyproject",
]

from __future__ import annotations

from tomlkit import parse
from tomlkit.toml_document import TOMLDocument

from ..cli import PyProjectFmtNamespace
from .build_system import fmt_build_system
from .project import fmt_project


def format_pyproject(opts: PyProjectFmtNamespace) -> str:
    text = opts.pyproject_toml.read_text()
    parsed: TOMLDocument = parse(text)
    _perform(parsed, opts)
    result = parsed.as_string().rstrip("\n")
    return f"{result}\n"


def _perform(parsed: TOMLDocument, opts: PyProjectFmtNamespace) -> None:
    fmt_build_system(parsed, opts)
    fmt_project(parsed, opts)


__all__ = ["format_pyproject"]

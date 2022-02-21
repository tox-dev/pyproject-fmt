from __future__ import annotations

from tomlkit import parse
from tomlkit.items import Array, String, Table
from tomlkit.toml_document import TOMLDocument

from ..cli import PyProjectFmtNamespace
from .requires import normalize_req


def format_pyproject(opts: PyProjectFmtNamespace) -> str:
    text = opts.pyproject_toml.read_text()
    parsed: TOMLDocument = parse(text)
    _perform(parsed)
    result = parsed.as_string()
    return result


def _perform(parsed: TOMLDocument) -> None:
    # 1. Normalize entries of the requires key
    build_system: Table = parsed["build-system"]  # type: ignore
    requires_array: Array = build_system["requires"]  # type: ignore
    for at in range(len(requires_array)):
        normalized = String.from_raw(normalize_req(str(requires_array[at])))
        requires_array[at] = normalized


__all__ = ["format_pyproject"]

from __future__ import annotations

from tomlkit import parse
from tomlkit.items import Array, String, Table
from tomlkit.toml_document import TOMLDocument

from ..cli import PyProjectFmtNamespace
from .requires import normalize_req
from .util import multiline_sorted_array, order_keys


def format_pyproject(opts: PyProjectFmtNamespace) -> str:
    text = opts.pyproject_toml.read_text()
    parsed: TOMLDocument = parse(text)
    _perform(parsed, opts)
    result = parsed.as_string().rstrip("\n")
    return f"{result}\n"


def _perform(parsed: TOMLDocument, opts: PyProjectFmtNamespace) -> None:
    _build_system(parsed, opts)


def _build_system(parsed: TOMLDocument, opts: PyProjectFmtNamespace) -> None:
    # 1. Normalize entries of the requires key
    build_system: Table = parsed["build-system"]  # type: ignore
    requires_array: Array = build_system["requires"]  # type: ignore
    for at in range(len(requires_array)):
        normalized = String.from_raw(normalize_req(str(requires_array[at])))
        requires_array[at] = normalized
    # 2. Make requires multiline and sorted
    multiline_sorted_array(requires_array, indent=opts.indent)
    # 2. Make backend-path multiline and sorted
    if "backend-path" in build_system:
        backend_path: Array = build_system["backend-path"]  # type: ignore
        multiline_sorted_array(backend_path, indent=opts.indent)
    # 3. Order build-system
    order_keys(build_system.value.body, ("build-backend", "requires", "backend-path"))


__all__ = ["format_pyproject"]

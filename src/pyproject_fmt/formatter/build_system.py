from __future__ import annotations

from typing import Optional, cast

from tomlkit.items import Array, Table
from tomlkit.toml_document import TOMLDocument

from ..cli import PyProjectFmtNamespace
from .pep508 import normalize_pep508_array
from .util import order_keys, sorted_array


def fmt_build_system(parsed: TOMLDocument, opts: PyProjectFmtNamespace) -> None:
    system = cast(Optional[Table], parsed.get("build-system"))
    if system is not None:
        normalize_pep508_array(cast(Optional[Array], system.get("requires")), opts.indent)
        sorted_array(cast(Optional[Array], system.get("backend-path")), indent=opts.indent)
        order_keys(system.value.body, ("build-backend", "requires", "backend-path"))


__all__ = ["fmt_build_system"]

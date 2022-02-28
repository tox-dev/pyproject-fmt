from __future__ import annotations

from typing import Optional, cast

from tomlkit.items import Array, Table
from tomlkit.toml_document import TOMLDocument

from .config import Config
from .pep508 import normalize_pep508_array
from .util import order_keys, sorted_array


def fmt_build_system(parsed: TOMLDocument, conf: Config) -> None:
    system = cast(Optional[Table], parsed.get("build-system"))
    if system is not None:
        normalize_pep508_array(cast(Optional[Array], system.get("requires")), conf.indent)
        sorted_array(cast(Optional[Array], system.get("backend-path")), indent=conf.indent)
        order_keys(system, ("build-backend", "requires", "backend-path"))


__all__ = [
    "fmt_build_system",
]

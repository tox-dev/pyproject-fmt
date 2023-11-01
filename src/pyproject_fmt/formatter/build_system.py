"""Logic related to formatting the build system."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, cast

from tomlkit.items import Array, Table

from .pep508 import normalize_pep508_array
from .util import ensure_newline_at_end, order_keys, sorted_array

if TYPE_CHECKING:
    from tomlkit.toml_document import TOMLDocument

    from .config import Config


def fmt_build_system(parsed: TOMLDocument, conf: Config) -> None:
    """
    Format the build system.

    :param parsed: the parsed document
    :param conf: configuration
    """
    system = cast(Optional[Table], parsed.get("build-system"))
    if system is not None:
        normalize_pep508_array(
            requires_array=cast(Optional[Array], system.get("requires")),
            indent=conf.indent,
            keep_full_version=conf.keep_full_version,
        )
        sorted_array(cast(Optional[Array], system.get("backend-path")), indent=conf.indent)
        order_keys(system, ("build-backend", "requires", "backend-path"))
        ensure_newline_at_end(system)


__all__ = [
    "fmt_build_system",
]

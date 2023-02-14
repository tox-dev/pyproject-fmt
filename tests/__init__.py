from __future__ import annotations

from typing import Callable

from tomlkit.toml_document import TOMLDocument

from pyproject_fmt.formatter.config import Config

Fmt = Callable[[Callable[[TOMLDocument, Config], None], str, str], None]

__all__ = [
    "Fmt",
]

from __future__ import annotations

from typing import Callable

from tomlkit.toml_document import TOMLDocument

from pyproject_fmt.cli import PyProjectFmtNamespace

Fmt = Callable[[Callable[[TOMLDocument, PyProjectFmtNamespace], None], str, str], None]

__all__ = ["Fmt"]

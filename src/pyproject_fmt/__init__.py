from __future__ import annotations

from ._version import version as __version__
from .cli import PyProjectFmtNamespace
from .formatter import format_pyproject

__all__ = [
    "__version__",
    "format_pyproject",
    "PyProjectFmtNamespace",
]

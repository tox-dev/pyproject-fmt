from __future__ import annotations

from ._version import version as __version__
from .formatter import format_pyproject
from .formatter.config import Config

__all__ = [
    "__version__",
    "Config",
    "format_pyproject",
]

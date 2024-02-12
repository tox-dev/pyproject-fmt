"""Format your pyproject.toml."""

from __future__ import annotations

from ._version import version as __version__
from .formatter import format_pyproject
from .formatter.config import Config, PyProjectConfig

__all__ = [
    "Config",
    "PyProjectConfig",
    "__version__",
    "format_pyproject",
]

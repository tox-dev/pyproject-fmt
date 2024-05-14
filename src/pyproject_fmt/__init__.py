"""Package root."""

from __future__ import annotations

from ._api import Settings, SettingsError, format_toml
from ._version import __version__

__all__ = [
    "Settings",
    "SettingsError",
    "__version__",
    "format_toml",
]

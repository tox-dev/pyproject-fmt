"""Defines configuration for the formatter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from packaging.version import Version

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


DEFAULT_INDENT: Final[int] = 2  #: default indentation level
DEFAULT_MAX_SUPPORTED_PYTHON: Final[str] = "3.12"  #: default maximum supported Python version


@dataclass(frozen=True)
class Config:
    """Configuration flags for the formatting."""

    pyproject_toml: Path
    toml: str  #: the text to format
    indent: int = DEFAULT_INDENT  #: indentation to apply
    keep_full_version: bool = False
    max_supported_python: Version = field(default_factory=lambda: Version(DEFAULT_MAX_SUPPORTED_PYTHON))


__all__ = [
    "Config",
    "DEFAULT_INDENT",
    "DEFAULT_MAX_SUPPORTED_PYTHON",
]

"""Defines configuration for the formatter."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


DEFAULT_INDENT: Final[int] = 2  #: default indentation level


@dataclass(frozen=True)
class Config:
    """Configuration flags for the formatting."""

    pyproject_toml: Path
    toml: str  #: the text to format
    indent: int = DEFAULT_INDENT  #: indentation to apply
    keep_full_version: bool = False


__all__ = [
    "Config",
    "DEFAULT_INDENT",
]

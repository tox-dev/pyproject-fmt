from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

if sys.version_info >= (3, 8):  # pragma: no cover (py38+)
    from typing import Final
else:  # pragma: no cover (<py38)
    from typing_extensions import Final


DEFAULT_INDENT: Final[int] = 2  #: default indentation level


@dataclass(frozen=True)
class Config:
    """Configuration flags for the formatting."""

    pyproject_toml: Path
    toml: str  #: the text to format
    indent: int = DEFAULT_INDENT  #: indentation to apply


__all__ = [
    "Config",
    "DEFAULT_INDENT",
]

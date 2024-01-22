"""Defines configuration for the formatter."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, TypedDict

from packaging.version import Version

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final


DEFAULT_INDENT: Final[int] = 2  #: default indentation level
DEFAULT_MAX_SUPPORTED_PYTHON: Final[str] = "3.12"  #: default maximum supported Python version


class PyProjectConfig(TypedDict):
    """Configuration defined in the ``tool.pyproject-fmt`` table in ``pyproject.toml``."""

    indent: int
    """Indentation level to apply."""

    keep_full_version: bool
    """Whether to keep the full version string or not."""

    max_supported_python: str
    """The maximum supported Python version."""


@dataclass(frozen=True)
class Config:
    """Configuration flags for the formatting."""

    pyproject_toml: Path
    toml: str  #: the text to format
    indent: int = DEFAULT_INDENT  #: indentation to apply
    keep_full_version: bool = False  #: whether to keep full dependency versions

    #: the maximum supported Python version
    max_supported_python: Version = field(default_factory=lambda: Version(DEFAULT_MAX_SUPPORTED_PYTHON))

    def with_overrides(self, overrides: PyProjectConfig) -> Config:
        """
        Create a new configuration with overrides applied.

        :param PyProjectConfig overrides: the overrides dictionary to apply from ``pyproject.toml``
        """
        max_supported_version = overrides.get("max_supported_python")
        return self.__class__(
            pyproject_toml=self.pyproject_toml,
            toml=self.toml,
            indent=overrides.get("indent", self.indent),
            keep_full_version=overrides.get("keep_full_version", self.keep_full_version),
            max_supported_python=Version(max_supported_version) if max_supported_version else self.max_supported_python,
        )


__all__ = [
    "Config",
    "DEFAULT_INDENT",
    "DEFAULT_MAX_SUPPORTED_PYTHON",
]

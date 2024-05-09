"""Defines configuration for the formatter."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING

from packaging.version import Version

if sys.version_info >= (3, 11):  # pragma: >=3.11 cover
    import tomllib
else:  # pragma: <3.11 cover
    import tomli as tomllib

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Final

DEFAULT_INDENT: Final[int] = 2  #: default indentation level
DEFAULT_MIN_SUPPORTED_PYTHON: Final[str] = "3.8"  #: default maximum supported Python version
DEFAULT_MAX_SUPPORTED_PYTHON: Final[str] = "3.12"  #: default maximum supported Python version


@dataclass(frozen=True)
class Config:
    """Configuration flags for the formatting."""

    pyproject_toml: Path
    indent: int  #: indentation to apply
    keep_full_version: bool  #: whether to keep full dependency versions
    #: the maximum supported Python version
    max_supported_python: Version
    #: the maximum supported Python version
    min_supported_python: Version

    @classmethod
    def from_file(  # noqa: PLR0913
        cls,
        *,
        filename: Path,
        indent: int,
        keep_full_version: bool,
        max_supported_python: Version,
        min_supported_python: Version,
    ) -> Config:
        """
        Create config from a toml file.

        :param filename: path to the toml file.
        :param indent: default indent level.
        :param keep_full_version: default keep full version.
        :param max_supported_python: default max supported python.
        :param min_supported_python: default min supported python.
        :return:
        """
        with filename.open("rb") as file_handler:
            config = tomllib.load(file_handler)
            if "tool" in config and "pyproject-fmt" in config["tool"]:
                for key, entry in config["tool"]["pyproject-fmt"].items():
                    if key == "indent":
                        indent = int(entry)
                    elif key == "keep_full_version":
                        keep_full_version = bool(entry)
                    elif key == "max_supported_python":
                        max_supported_python = Version(entry)
                    elif key == "min_supported_python":  # pragma: no branch
                        min_supported_python = Version(entry)
        return cls(
            pyproject_toml=filename,
            indent=indent,
            keep_full_version=keep_full_version,
            max_supported_python=max_supported_python,
            min_supported_python=min_supported_python,
        )

    @property
    def toml(self) -> str:
        """:return: the toml files content"""
        return self.pyproject_toml.read_text(encoding="utf-8")


__all__ = [
    "DEFAULT_INDENT",
    "DEFAULT_MAX_SUPPORTED_PYTHON",
    "DEFAULT_MIN_SUPPORTED_PYTHON",
    "Config",
]

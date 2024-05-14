"""Wrapper for ``pyproject_fmt_rust`` adding default and TOML configuration."""

from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Any

import pyproject_fmt_rust

if sys.version_info >= (3, 11):  # pragma: >=3.11 cover
    from typing import Self

    import tomllib
else:  # pragma: <3.11 cover
    import tomli as tomllib

    if TYPE_CHECKING:  # pragma: no cover
        from typing_extensions import Self


class SettingsError(ValueError):
    """Exception for invalid ``pyproject-fmt`` configurations."""


@dataclasses.dataclass
class Settings:
    """
    Dataclass for formatting parameters.

    Attributes correspond to options in the CLI.
    """

    column_width: int = 1
    indent: int = 2
    keep_full_version: bool = False
    max_supported_python: tuple[int, int] = (3, 12)
    min_supported_python: tuple[int, int] = (3, 8)

    def read_toml(self, pyproject_toml: str) -> Self:
        """Create a copy with attributes overwritten by the TOML configuration."""
        return self._read_toml(tomllib.loads(pyproject_toml))

    def _read_toml(self, pyproject: dict[str, Any], exc: type[Exception] = SettingsError) -> Self:
        copy = self.__class__(**dataclasses.asdict(self))

        if "tool" in pyproject and "pyproject-fmt" in pyproject["tool"]:
            for key, entry in pyproject["tool"]["pyproject-fmt"].items():
                if key == "column_width":
                    copy.column_width = int(entry)
                elif key == "indent":
                    copy.indent = int(entry)
                elif key == "keep_full_version":
                    copy.keep_full_version = bool(entry)
                elif key == "max_supported_python":
                    copy.max_supported_python = self._version_argument(entry, exc)

        return copy

    @staticmethod
    def _version_argument(got: str, exc: type[Exception] = SettingsError) -> tuple[int, int]:
        # "Protected" method: private for the outside world, but used internally.
        parts = got.split(".")
        if len(parts) != 2:  # noqa: PLR2004
            msg = f"invalid version: {got}, must be e.g. 3.12"
            raise exc(msg)
        try:
            return int(parts[0]), int(parts[1])
        except ValueError as e:
            msg = f"invalid version: {got} due {e!r}, must be e.g. 3.12"
            raise exc(msg) from e

    def _as_native(self) -> pyproject_fmt_rust.Settings:
        # "Protected" method: private for the outside world, but used internally.
        return pyproject_fmt_rust.Settings(
            column_width=self.column_width,
            indent=self.indent,
            keep_full_version=self.keep_full_version,
            max_supported_python=self.max_supported_python,
            min_supported_python=self.min_supported_python,
        )


def format_toml(text: str, settings: Settings | None = None) -> str:
    """Format the given ``pyproject.toml`` text."""
    config = (settings or Settings()).read_toml(text)
    return pyproject_fmt_rust.format_toml(text, config._as_native())  # noqa: SLF001


__all__ = ["Settings", "SettingsError", "format_toml"]

from __future__ import annotations

from typing import Protocol


class Fmt(Protocol):
    def __call__(
        self,
        start: str,
        expected: str,
        *,
        indent: int = ...,
        keep_full_version: bool = ...,
        max_supported_python: tuple[int, int] = ...,
    ) -> None: ...


__all__ = [
    "Fmt",
]

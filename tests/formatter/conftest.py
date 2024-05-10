from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from pyproject_fmt._lib import format_toml

if TYPE_CHECKING:
    from tests import Fmt


@pytest.fixture()
def fmt() -> Fmt:
    def _func(
        start: str,
        expected: str,
        *,
        column_width: int = 1,
        indent: int = 2,
        keep_full_version: bool = False,
        max_supported_python: tuple[int, int] = (3, 12),
        min_supported_python: tuple[int, int] = (3, 8),
    ) -> None:
        result = format_toml(
            dedent(start),
            column_width=column_width,
            indent=indent,
            keep_full_version=keep_full_version,
            max_supported_python=max_supported_python,
            min_supported_python=min_supported_python,
        )
        expected = dedent(expected)
        assert result == expected

    return _func

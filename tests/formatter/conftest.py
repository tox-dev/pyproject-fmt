from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Callable

import pytest

from pyproject_fmt.formatter import format_pyproject
from pyproject_fmt.formatter.config import Config

if TYPE_CHECKING:
    from pytest_mock import MockerFixture
    from tomlkit.toml_document import TOMLDocument

    from tests import Fmt


@pytest.fixture()
def fmt(monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture, tmp_path: Path) -> Fmt:
    def _func(
        formatter: Callable[[TOMLDocument, Config], None],
        start: str | Config,
        expected: str,
    ) -> None:
        mocker.patch("pyproject_fmt.formatter._perform", formatter)
        opts = Config(pyproject_toml=Path(), toml=dedent(start)) if isinstance(start, str) else start
        monkeypatch.chdir(tmp_path)
        result = format_pyproject(opts)

        expected = dedent(expected)
        assert result == expected

    return _func

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Callable

import pytest
from pytest_mock import MockerFixture
from tomlkit.toml_document import TOMLDocument

from pyproject_fmt.formatter import format_pyproject
from pyproject_fmt.formatter.config import Config
from tests import Fmt


@pytest.fixture()
def fmt(mocker: MockerFixture) -> Fmt:
    def _func(formatter: Callable[[TOMLDocument, Config], None], start: str, expected: str) -> None:
        mocker.patch("pyproject_fmt.formatter._perform", formatter)
        opts = Config(pyproject_toml=Path(), toml=dedent(start))
        result = format_pyproject(opts)

        expected = dedent(expected)
        assert result == expected

    return _func

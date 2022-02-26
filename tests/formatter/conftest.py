from __future__ import annotations

from textwrap import dedent
from typing import Callable

import pytest
from pytest_mock import MockerFixture
from tomlkit.toml_document import TOMLDocument

from pyproject_fmt.cli import PyProjectFmtNamespace
from pyproject_fmt.formatter import format_pyproject
from tests import Fmt


@pytest.fixture()
def fmt(mocker: MockerFixture) -> Fmt:
    def _func(formatter: Callable[[TOMLDocument, PyProjectFmtNamespace], None], start: str, expected: str) -> None:
        mocker.patch("pyproject_fmt.formatter._perform", formatter)
        result = format_pyproject(dedent(start), PyProjectFmtNamespace())

        expected = dedent(expected)
        assert result == expected

    return _func

from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import Callable

import pytest
from pytest_mock import MockerFixture
from tomlkit.toml_document import TOMLDocument

from pyproject_fmt.cli import PyProjectFmtNamespace
from pyproject_fmt.formatter import format_pyproject
from tests import Fmt


@pytest.fixture()
def fmt(tmp_path: Path, mocker: MockerFixture) -> Fmt:
    def _func(formatter: Callable[[TOMLDocument, PyProjectFmtNamespace], None], start: str, expected: str) -> None:
        mocker.patch("pyproject_fmt.formatter._perform", formatter)
        toml = tmp_path / "a.toml"
        toml.write_text(dedent(start))
        opts = PyProjectFmtNamespace(pyproject_toml=tmp_path / "a.toml")
        result = format_pyproject(opts)

        expected = dedent(expected)
        assert result == expected

    return _func

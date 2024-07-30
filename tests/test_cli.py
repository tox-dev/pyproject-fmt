from __future__ import annotations

import io
import os
import sys
from importlib.metadata import version
from stat import S_IREAD, S_IWRITE
from typing import TYPE_CHECKING

import pytest

from pyproject_fmt.cli import cli_args

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as context:
        cli_args(["--version"])
    assert context.value.code == 0
    out, _err = capsys.readouterr()
    assert out == f"pyproject-fmt ({version('pyproject-fmt')})\n"


def test_cli_invalid_version(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text("")
    with pytest.raises(SystemExit) as context:
        cli_args([str(path), "--max-supported-python", "3"])
    assert context.value.code == 2
    out, err = capsys.readouterr()
    assert not out
    assert "error: argument --max-supported-python: invalid version: 3, must be e.g. 3.12\n" in err


def test_cli_invalid_version_value(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    path = tmp_path / "pyproject.toml"
    path.write_text("")
    with pytest.raises(SystemExit) as context:
        cli_args([str(path), "--max-supported-python", "a.1"])
    assert context.value.code == 2
    out, err = capsys.readouterr()
    assert not out
    assert (
        "error: argument --max-supported-python: invalid version: a.1 due "
        'ValueError("invalid literal for int() with base 10:'
    ) in err


def test_cli_pyproject_toml_ok(tmp_path: Path) -> None:
    path = tmp_path / "tox.ini"
    path.write_text("")
    result = cli_args([str(path)])
    assert len(result) == 1
    assert result[0]


def test_cli_inputs_ok(tmp_path: Path) -> None:
    paths = []
    for filename in ("tox.ini", "tox2.ini", "tox3.ini"):
        path = tmp_path / filename
        path.write_text("")
        paths.append(path)
    result = cli_args([*map(str, paths)])
    assert len(result) == 3


def test_cli_pyproject_toml_stdin(mocker: MockerFixture) -> None:
    mocker.patch("pyproject_fmt.cli.sys.stdin", io.StringIO(""))
    result = cli_args(["-"])
    assert len(result) == 1
    assert result[0].pyproject_toml is None
    assert not result[0].toml


def test_cli_pyproject_toml_not_exists(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as context:
        cli_args([str(tmp_path / "tox.ini")])
    assert context.value.code != 0
    out, err = capsys.readouterr()
    assert not out
    assert "argument inputs: path does not exist" in err


def test_cli_pyproject_toml_not_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = tmp_path / "temp"
    os.mkfifo(path)
    with pytest.raises(SystemExit) as context:
        cli_args([str(path)])
    assert context.value.code != 0
    out, err = capsys.readouterr()
    assert not out
    assert "argument inputs: path is not a file" in err


@pytest.mark.parametrize(("flag", "error"), [(S_IREAD, "write"), (S_IWRITE, "read")])
@pytest.mark.skipif(
    sys.platform == "win32",
    reason="On Windows files cannot be read only, only folders",
)
def test_cli_pyproject_toml_permission_fail(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    flag: int,
    error: str,
) -> None:
    path = tmp_path / "tox.ini"
    path.write_text("")
    path.chmod(flag)
    try:
        with pytest.raises(SystemExit) as context:
            cli_args([str(path)])
    finally:
        path.chmod(S_IWRITE | S_IREAD)
    assert context.value.code != 0
    out, err = capsys.readouterr()
    assert not out
    assert f"argument inputs: cannot {error} path" in err


def test_pyproject_toml_resolved(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "tox.ini"
    path.write_text("")
    result = cli_args(["tox.ini"])
    assert len(result) == 1


def test_pyproject_toml_dir(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("")
    cli_args([str(tmp_path)])

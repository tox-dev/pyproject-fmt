from __future__ import annotations

import os
import sys
from pathlib import Path
from stat import S_IREAD, S_IWRITE

import pytest

from pyproject_fmt.cli import cli_args


def test_cli_pyproject_toml_ok(tmp_path: Path) -> None:
    path = tmp_path / "tox.ini"
    path.write_text("")
    result = cli_args([str(path)])
    assert result.inputs == [path]


def test_cli_inputs_ok(tmp_path: Path) -> None:
    paths = []
    for filename in ("tox.ini", "tox2.ini", "tox3.ini"):
        path = tmp_path / filename
        path.write_text("")
        paths.append(path)
    result = cli_args([*map(str, paths)])
    assert result.inputs == paths


def test_cli_pyproject_toml_not_exists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as context:
        cli_args([str(tmp_path / "tox.ini")])
    assert context.value.code != 0
    out, err = capsys.readouterr()
    assert not out
    assert "argument inputs: path does not exist" in err


def test_cli_pyproject_toml_not_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "temp"
    os.mkfifo(path)
    with pytest.raises(SystemExit) as context:
        cli_args([str(path)])
    assert context.value.code != 0
    out, err = capsys.readouterr()
    assert not out
    assert "argument inputs: path is not a file" in err


@pytest.mark.parametrize(("flag", "error"), [(S_IREAD, "write"), (S_IWRITE, "read")])
@pytest.mark.skipif(sys.platform == "win32", reason="On Windows files cannot be read only, only folders")
def test_cli_pyproject_toml_permission_fail(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], flag: int, error: str
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


def test_pyproject_toml_resolved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "tox.ini"
    path.write_text("")
    result = cli_args(["tox.ini"])
    assert result.inputs == [path]


def test_pyproject_toml_dir(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("")
    cli_args([str(tmp_path)])

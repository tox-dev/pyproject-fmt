from __future__ import annotations

import sys
from pathlib import Path
from stat import S_IREAD, S_IWRITE

import pytest

from pyproject_fmt.cli import cli_args


def test_cli_pyproject_toml_ok(tmp_path: Path) -> None:
    path = tmp_path / "tox.ini"
    path.write_text("")
    result = cli_args([str(path)])
    assert result.pyproject_toml == path


def test_cli_pyproject_toml_not_exists(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as context:
        cli_args([str(tmp_path / "tox.ini")])
    assert context.value.code != 0
    out, err = capsys.readouterr()
    assert not out
    assert "argument pyproject_toml: path does not exist" in err


def test_cli_pyproject_toml_not_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as context:
        cli_args([str(tmp_path)])
    assert context.value.code != 0
    out, err = capsys.readouterr()
    assert not out
    assert "argument pyproject_toml: path is not a file" in err


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
    assert f"argument pyproject_toml: cannot {error} path" in err


def test_pyproject_toml_resolved(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "tox.ini"
    path.write_text("")
    result = cli_args(["tox.ini"])
    assert result.pyproject_toml == path

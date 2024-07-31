from __future__ import annotations

import difflib
from textwrap import dedent
from typing import TYPE_CHECKING, Any

import pytest

from pyproject_fmt import __version__
from pyproject_fmt.__main__ import GREEN, RED, RESET, color_diff, run

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


def test_version() -> None:
    assert isinstance(__version__, str)


def test_color_diff() -> None:
    # Arrange
    before = """
    abc
    def
    ghi
"""
    after = """
    abc
    abc
    def
"""
    diff = difflib.unified_diff(before.splitlines(), after.splitlines())
    expected_lines = f"""
{RED}---
{RESET}
{GREEN}+++
{RESET}
@@ -1,4 +1,4 @@


     abc
{GREEN}+    abc{RESET}
     def
{RED}-    ghi{RESET}
""".strip().splitlines()

    # Act
    found_diff = color_diff(diff)

    # Assert
    output_lines = [line.rstrip() for line in "\n".join(found_diff).splitlines()]
    assert output_lines == expected_lines


def no_color(diff: Any) -> Any:
    return diff


@pytest.mark.parametrize(
    "in_place",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize(
    "check",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize(
    "cwd",
    [
        True,
        False,
    ],
)
@pytest.mark.parametrize(
    ("start", "outcome", "output"),
    [
        (
            '[build-system]\nrequires = [\n  "hatchling>=0.14",\n]\n',
            '[build-system]\nrequires = [\n  "hatchling>=0.14",\n]\n',
            "no change for {0}\n",
        ),
        (
            '[build-system]\nrequires = ["hatchling>=0.14.0"]',
            '[build-system]\nrequires = [ "hatchling>=0.14" ]\n',
            "--- {0}\n\n+++ {0}\n\n@@ -1,2 +1,2 @@\n\n [build-system]\n-requires = "
            '["hatchling>=0.14.0"]\n+requires = [ "hatchling>=0.14" ]\n',
        ),
    ],
)
def test_main(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    in_place: bool,
    start: str,
    outcome: str,
    output: str,
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
    cwd: bool,
    check: bool,
) -> None:
    mocker.patch("pyproject_fmt.__main__.color_diff", no_color)
    if cwd:
        monkeypatch.chdir(tmp_path)
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(start)
    args = [str(pyproject_toml)]
    if not in_place:
        args.append("--stdout")

    if check:
        args.append("--check")

        if not in_place:
            with pytest.raises(SystemExit):
                run(args)
            assert pyproject_toml.read_text() == start
            return

    result = run(args)
    assert result == (0 if start == outcome else 1)

    out, err = capsys.readouterr()
    assert not err

    if check:
        assert pyproject_toml.read_text() == start
    elif in_place:
        name = "pyproject.toml" if cwd else str(tmp_path / "pyproject.toml")
        output = output.format(name)
        assert pyproject_toml.read_text() == outcome
        assert out == output
    else:
        assert out == outcome


@pytest.mark.parametrize("indent", [0, 2, 4])
def test_indent(tmp_path: Path, indent: int) -> None:
    start = """\
    [build-system]
    requires = [
        "A",
    ]
    """

    expected = f"""\
    [build-system]
    requires = [
    {" " * indent}"a",
    ]
    """
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(dedent(start))
    args = [str(pyproject_toml), "--indent", str(indent)]
    run(args)
    output = pyproject_toml.read_text()
    assert output == dedent(expected)


def test_keep_full_version_cli(tmp_path: Path) -> None:
    start = """\
    [build-system]
    requires = [
      "a==1.0.0",
    ]

    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "a==1.0.0",
    ]
    optional-dependencies.docs = [
      "b==2.0.0",
    ]
    """
    pyproject_toml = tmp_path / "pyproject.toml"
    pyproject_toml.write_text(dedent(start))
    args = [str(pyproject_toml), "--keep-full-version", "--max-supported-python", "3.8"]
    run(args)
    output = pyproject_toml.read_text()
    assert output == dedent(start)


def test_pyproject_toml_config(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    txt = """
    [project]
    keywords = [
      "A",
    ]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
    ]
    dynamic = [
      "B",
    ]
    dependencies = [
      "requests>=2.0",
    ]

    [tool.pyproject-fmt]
    column_width = 20
    indent = 4
    keep_full_version = true
    max_supported_python = "3.10"
    ignore_extra = true
    """
    filename = tmp_path / "pyproject.toml"
    filename.write_text(dedent(txt))
    run([str(filename)])

    expected = """\
    [project]
    keywords = [
        "A",
    ]
    classifiers = [
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ]
    dynamic = [
        "B",
    ]
    dependencies = [
        "requests>=2.0",
    ]

    [tool.pyproject-fmt]
    column_width = 20
    indent = 4
    keep_full_version = true
    max_supported_python = "3.10"
    ignore_extra = true
    """
    got = filename.read_text()
    assert got == dedent(expected)
    out, err = capsys.readouterr()
    assert out
    assert not err


def test_pyproject_ftm_api_changed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    txt = """
    [project]
    requires-python = "==3.12"
    """
    filename = tmp_path / "pyproject.toml"
    filename.write_text(dedent(txt))
    res = run([str(filename), "--no-print-diff", "--column-width", "20"])

    assert res == 1

    got = filename.read_text()
    expected = """\
    [project]
    requires-python = "==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    """
    assert got == dedent(expected)

    out, err = capsys.readouterr()
    assert not out
    assert not err


def test_pyproject_ftm_api_no_change(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    txt = """\
    [project]
    requires-python = "==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    """
    filename = tmp_path / "pyproject.toml"
    filename.write_text(dedent(txt))
    res = run([str(filename), "--no-print-diff"])

    assert res == 0

    got = filename.read_text()

    assert got == dedent(txt)

    out, err = capsys.readouterr()
    assert not out
    assert not err

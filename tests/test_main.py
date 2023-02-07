from __future__ import annotations

import difflib
from pathlib import Path
from typing import Any

import pytest

import pyproject_fmt.__main__
from pyproject_fmt.__main__ import GREEN, RED, RESET, color_diff, run


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
            '[build-system]\nrequires = [\n  "hatchling>=0.14",\n]\n',
            "--- {0}\n\n+++ {0}\n\n@@ -1,2 +1,4 @@\n\n [build-system]\n-requires = "
            '["hatchling>=0.14.0"]\n+requires = [\n+  "hatchling>=0.14",\n+]\n',
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
    cwd: bool,
    check: bool,
) -> None:
    monkeypatch.setattr(pyproject_fmt.__main__, "color_diff", no_color)
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

from pathlib import Path
from textwrap import dedent

from pyproject_fmt.cli import PyProjectFmtNamespace
from pyproject_fmt.formatter import format_pyproject


def test_build_backend(tmp_path: Path) -> None:
    txt = """
    [build-system]
    backend-path = ['A', 'B']
    requires = [
      # start
      # two
      "A",
      "B", # c # d follow-up comment
      "C", # magic
      "D", # a
      "E", # b
      "F", # comment ok
    ]
    build-backend = "hatchling.build"
    """
    toml = tmp_path / "a.toml"
    toml.write_text(dedent(txt))
    result = format_pyproject(PyProjectFmtNamespace(pyproject_toml=toml))
    expected = """
    [build-system]
    build-backend = "hatchling.build"
    requires = [
      # start
      # two
      "A",
      "B", # c # d follow-up comment
      "C", # magic
      "D", # a
      "E", # b
      "F", # comment ok
    ]
    backend-path = [
      'A',
      'B',
    ]
    """

    assert result == dedent(expected)

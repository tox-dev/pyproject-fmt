from __future__ import annotations

from textwrap import dedent

import pytest

from pyproject_fmt import Settings, SettingsError, format_toml


def test_default_config() -> None:
    txt = """\
    [project]
    keywords = ["A"]
    classifiers = ["Programming Language :: Python :: 3 :: Only"]
    """
    expected = dedent(
        """\
        [project]
        keywords = [
          "A",
        ]
        classifiers = [
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
        ]
        """
    )
    got = format_toml(txt)
    assert got == expected


def test_pyproject_toml_config() -> None:
    txt = """\
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

    expected = dedent(
        """\
        [project]
        keywords = [
            "A",
        ]
        classifiers = [
            "Programming Language :: Python :: 3 :: Only",
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
    )
    got = format_toml(txt, Settings(min_supported_python=(3, 9)))
    assert got == expected


@pytest.mark.parametrize("version", ["3", "3.X"])
def test_invalid_version(version: str) -> None:
    with pytest.raises(SettingsError, match=f"invalid version: {version}"):
        Settings._version_argument(version)  # noqa: SLF001

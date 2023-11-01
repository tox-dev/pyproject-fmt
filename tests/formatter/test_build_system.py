from __future__ import annotations

from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from pyproject_fmt.formatter.build_system import fmt_build_system
from pyproject_fmt.formatter.config import Config

if TYPE_CHECKING:
    from tests import Fmt


def test_build_system_missing(fmt: Fmt) -> None:
    fmt(fmt_build_system, "", "\n")


def test_backend_path(fmt: Fmt) -> None:
    start = "[build-system]\nbackend-path = ['A-B', 'AA']"
    expected = "[build-system]\nbackend-path = [\n  'A-B',\n  'AA',\n]\n"
    fmt(fmt_build_system, start, expected)


def test_requires(fmt: Fmt) -> None:
    txt = """
        [build-system]
        requires = [
        # start
        # two
        "A-B", "A>1",     # c # d
        # follow-up comment
        "C",
        # magic
        "D"  ,   # a
        "E",  # b
        "F" # comment
            # ok
        ]
        """

    expected = """
        [build-system]
        requires = [
          # start
          # two
          "A>1", # c # d follow-up comment
          "A-B",
          "C", # magic
          "D", # a
          "E", # b
          "F", # comment ok
        ]
        """

    fmt(fmt_build_system, txt, expected)


def test_build_backend_order(fmt: Fmt) -> None:
    txt = """
    [build-system]
    backend-path = ['A']
    requires = ["A"]
    build-backend = "hatchling.build"
    """

    expected = """
    [build-system]
    build-backend = "hatchling.build"
    requires = [
      "A",
    ]
    backend-path = [
      'A',
    ]
    """

    fmt(fmt_build_system, txt, expected)


@pytest.mark.parametrize("indent", [0, 2, 4])
def test_indent(fmt: Fmt, indent: int) -> None:
    txt = """
    [build-system]
    requires = [
    "A",
    "B",
    ]
    backend-path = [
    "C",
    ]
    """
    expected = f"""
    [build-system]
    requires = [
    {" " * indent}"A",
    {" " * indent}"B",
    ]
    backend-path = [
    {" " * indent}"C",
    ]
    """
    config = Config(pyproject_toml=Path(), toml=dedent(txt), indent=indent)
    fmt(fmt_build_system, config, expected)


def test_keep_full_version_on(fmt: Fmt) -> None:
    txt = """
    [build-system]
    requires = [
      "A==1.0.0",
    ]
    """
    config = Config(pyproject_toml=Path(), toml=dedent(txt), indent=2, keep_full_version=True)
    fmt(fmt_build_system, config, txt)


def test_keep_full_version_off(fmt: Fmt) -> None:
    txt = """
    [build-system]
    requires = [
      "A==1.0.0",
    ]
    """
    expected = """
    [build-system]
    requires = [
      "A==1",
    ]
    """
    config = Config(pyproject_toml=Path(), toml=dedent(txt), indent=2, keep_full_version=False)
    fmt(fmt_build_system, config, expected)

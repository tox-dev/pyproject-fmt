from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tests import Fmt


def test_build_system_missing(fmt: Fmt) -> None:
    fmt("", "\n")


def test_backend_path(fmt: Fmt) -> None:
    start = "[build-system]\nbackend-path = ['A-B', 'AA']"
    expected = "[build-system]\nbackend-path = [\n  'A-B',\n  'AA',\n]\n"
    fmt(start, expected)


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

    expected = """\
        [build-system]
        requires = [
          "A>1", # c # d
          # start
          # two
          "A-B",
          # follow-up comment
          "C",
          # magic
          "D", # a
          "E", # b
          "F", # comment
          # ok
        ]
        """

    fmt(txt, expected)


def test_build_backend_order(fmt: Fmt) -> None:
    txt = """
    [build-system]
    backend-path = ['A']
    requires = ["A"]
    build-backend = "hatchling.build"
    """

    expected = """\
    [build-system]
    build-backend = "hatchling.build"
    requires = [
      "A",
    ]
    backend-path = [
      'A',
    ]
    """

    fmt(txt, expected)


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
    expected = f"""\
    [build-system]
    requires = [
    {" " * indent}"A",
    {" " * indent}"B",
    ]
    backend-path = [
    {" " * indent}"C",
    ]
    """
    fmt(txt, expected, indent=indent)


def test_keep_full_version_on(fmt: Fmt) -> None:
    txt = """\
    [build-system]
    requires = [
      "A==1.0.0",
    ]
    """
    fmt(txt, txt, keep_full_version=True)


def test_keep_full_version_off(fmt: Fmt) -> None:
    txt = """
    [build-system]
    requires = [
      "A==1.0.0",
    ]
    """
    expected = """\
    [build-system]
    requires = [
      "A==1",
    ]
    """
    fmt(txt, expected, indent=2, keep_full_version=False)

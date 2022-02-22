from __future__ import annotations

from pyproject_fmt.formatter.build_system import fmt_build_system
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

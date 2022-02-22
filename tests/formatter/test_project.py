from __future__ import annotations

from pyproject_fmt.formatter.project import fmt_project
from tests import Fmt


def test_project_name(fmt: Fmt) -> None:
    fmt(fmt_project, "[project]\nname='a-b'", '[project]\nname="a_b"\n')


def test_project_dependencies(fmt: Fmt) -> None:
    start = '[project]\ndependencies=["pytest","pytest-cov",]'
    expected = '[project]\ndependencies=[\n  "pytest",\n  "pytest-cov",\n]\n'
    fmt(fmt_project, start, expected)


def test_project_description(fmt: Fmt) -> None:
    start = '[project]\ndescription=" Magical stuff\t"'
    expected = '[project]\ndescription="Magical stuff"\n'
    fmt(fmt_project, start, expected)


def test_project_scripts(fmt: Fmt) -> None:
    start = """
    [project.scripts]
    c = "d"
    a = "b"
    """
    expected = """
    [project.scripts]
    a = "b"
    c = "d"
    """
    fmt(fmt_project, start, expected)


def test_project_optional_dependencies(fmt: Fmt) -> None:
    start = """
    [project.optional-dependencies]
    test = ["B", "A"]
    docs = [ "C",
    "D"]
    """
    expected = """
    [project.optional-dependencies]
    docs = [
      "C",
      "D",
    ]
    test = [
      "A",
      "B",
    ]
    """
    fmt(fmt_project, start, expected)


def test_entry_points(fmt: Fmt) -> None:
    start = """
    [project.entry-points]
    beta = {C = "c", D = "d"}
    alpha = {B = "b", "A.A" = "a"}
    """
    expected = """
    [project.entry-points]
    alpha = {"A.A" = "a",B = "b"
    }
    beta = {C = "c",D = "d"
    }
    """
    fmt(fmt_project, start, expected)

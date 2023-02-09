from __future__ import annotations

import pytest

from pyproject_fmt.formatter.project import fmt_project
from tests import Fmt


@pytest.mark.parametrize(
    "value",
    [
        "[project]\nname='a-b'",
        "[project]\nname='A_B'",
        "[project]\nname='a.-..-__B'",
    ],
)
def test_project_name(fmt: Fmt, value: str) -> None:
    fmt(fmt_project, value, '[project]\nname="a-b"\n')


def test_project_dependencies(fmt: Fmt) -> None:
    start = '[project]\ndependencies=["pytest","pytest-cov",]'
    expected = '[project]\ndependencies=[\n  "pytest",\n  "pytest-cov",\n]\n'
    fmt(fmt_project, start, expected)


def test_project_dependencies_with_double_quotes(fmt: Fmt) -> None:
    start = """
    [project]
    dependencies = [
        'packaging>=20.0;python_version>"3.4"',
        "appdirs"
    ]
    """
    expected = """
    [project]
    dependencies = [
      "appdirs",
      'packaging>=20; python_version > "3.4"',
    ]
    """
    fmt(fmt_project, start, expected)


def test_project_dependencies_with_mixed_quotes(fmt: Fmt) -> None:
    start = """
    [project]
    dependencies = [
        "packaging>=20.0;python_version>\\"3.4\\" and python_version != '3.5'",
        "foobar@ git+https://weird-vcs/w/index.php?param=org'repo ; python_version == '2.7'",
        "appdirs"
    ]
    """
    expected = """
    [project]
    dependencies = [
      "appdirs",
      "foobar@ git+https://weird-vcs/w/index.php?param=org'repo ; python_version == \\"2.7\\"",
      'packaging>=20; python_version > "3.4" and python_version != "3.5"',
    ]
    """
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
    alpha = {"A.A" = "a",B = "b"}
    beta = {C = "c",D = "d"}
    """
    fmt(fmt_project, start, expected)

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from tests import Fmt


@pytest.mark.parametrize(
    "value",
    [
        "[project]\nname='a.b'",
        "[project]\nname='A_B'",
        "[project]\nname='a.-..-__B'",
    ],
)
def test_project_name(fmt: Fmt, value: str) -> None:
    txt = """\
    [project]
    name = "a-b"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    """
    fmt(value, txt, max_supported_python=(3, 8))


def test_project_classifiers(fmt: Fmt) -> None:
    start = """
    [project]
    classifiers = [
      "Operating System :: OS Independent",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3 :: Only",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.12",
      "Programming Language :: Python :: 3.8",
      "License :: OSI Approved :: MIT License",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.11",
    ]
    """
    expected = """\
    [project]
    classifiers = [
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(start, expected)


def test_project_dependencies(fmt: Fmt) -> None:
    start = '[project]\ndependencies=["pytest","pytest-cov",]'
    expected = """\
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "pytest",
      "pytest-cov",
    ]
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_project_dependencies_with_double_quotes(fmt: Fmt) -> None:
    start = """
    [project]
    dependencies = [
        'packaging>=20.0;python_version>"3.4"',
        "appdirs"
    ]
    """
    expected = """\
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "appdirs",
      "packaging>=20; python_version > \\"3.4\\"",
    ]
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_project_dependencies_with_mixed_quotes(fmt: Fmt) -> None:
    start = """
    [project]
    dependencies = [
        "packaging>=20.0;python_version>\\"3.4\\" and python_version != '3.5'",
        "foobar@ git+https://weird-vcs/w/index.php?param=org'repo ; python_version == '2.7'",
        "appdirs"
    ]
    """
    expected = """\
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "appdirs",
      "foobar@ git+https://weird-vcs/w/index.php?param=org'repo ; python_version == \\"2.7\\"",
      "packaging>=20; python_version > \\"3.4\\" and python_version != \\"3.5\\"",
    ]
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_project_description(fmt: Fmt) -> None:
    start = '[project]\ndescription=" Magical stuff\t"'
    expected = """\
        [project]
        description = "Magical stuff"
        classifiers = [
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.8",
        ]
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_project_description_multiline(fmt: Fmt) -> None:
    start = '''\
        [project]
        description="""A multi-line
                       description."""
    '''
    expected = """\
        [project]
        description = "A multi-line description."
        classifiers = [
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.8",
        ]
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_project_scripts(fmt: Fmt) -> None:
    start = """
    [project.scripts]
    c = "d"
    a = "b"
    """
    expected = """\
    [project.scripts]
    a = "b"
    c = "d"
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_project_optional_dependencies(fmt: Fmt) -> None:
    start = """
    [project.optional-dependencies]
    test = ["B", "A"]
    docs = [ "C",
    "D"]
    """
    expected = """\
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
    fmt(start, expected, max_supported_python=(3, 8))


def test_entry_points(fmt: Fmt) -> None:
    start = """
    [project.entry-points]
    beta = {C = "c", D = "d"}
    alpha = {B = "b", "A.A" = "a"}
    """
    expected = """\
    [project.entry-points]
    alpha = {"A.A" = "a",B = "b"}
    beta = {C = "c",D = "d"}
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_classifier_none(fmt: Fmt) -> None:
    start = """
    [project]
    """
    expected = """\
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_classifier_lt(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<3.7"
    """
    expected = """\
    [project]
    requires-python = "<3.7"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
    ]
    """
    fmt(start, expected, max_supported_python=(3, 8))


def test_classifier_gt(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = ">3.6"
    """
    expected = """\
    [project]
    requires-python = ">3.6"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(start, expected)


def test_classifier_gte(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = ">=3.6"
    """
    expected = """\
    [project]
    requires-python = ">=3.6"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(start, expected)


def test_classifier_eq(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python="==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    expected = """\
    [project]
    requires-python = "==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(start, expected)


def test_classifier_neq(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "!=3.9"
    """
    expected = """\
    [project]
    requires-python = "!=3.9"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(start, expected)


def test_classifier_range(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python=">=3.7,<3.13"
    """
    expected = """\
    [project]
    requires-python = ">=3.7,<3.13"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(start, expected)


def test_classifier_range_neq(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<=3.12,!=3.9,>=3.8"
    """
    expected = """\
    [project]
    requires-python = "<=3.12,!=3.9,>=3.8"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(start, expected)


def test_classifier_high_range(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<=3.13,>3.10"
    """
    expected = """\
    [project]
    requires-python = "<=3.13,>3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
      "Programming Language :: Python :: 3.13",
    ]
    """
    fmt(start, expected)


def test_classifier_upper_bound(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<3.9"
    classifiers = [
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
    ]
    """
    expected = """\
    [project]
    requires-python = "<3.9"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    """
    fmt(start, expected)


def test_classifier_two_upper_bounds(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<3.9,<=3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
    ]
    """
    expected = """\
    [project]
    requires-python = "<3.9,<=3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    """
    fmt(start, expected)


def test_classifier_prerelease(fmt: Fmt) -> None:
    txt = """
    [project]
    requires-python = ">=3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    expected = """\
    [project]
    requires-python = ">=3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
      "Programming Language :: Python :: 3.13",
      "Programming Language :: Python :: 3.14",
      "Programming Language :: Python :: 3.15",
    ]
    """
    fmt(txt, expected, max_supported_python=(3, 15))


@pytest.mark.parametrize("indent", [0, 2, 4])
def test_indent(fmt: Fmt, indent: int) -> None:
    txt = """
    [project]
    keywords = [
      "A",
    ]
    dynamic = [
      "B",
    ]
    classifiers = [
      "C",
    ]
    dependencies = [
      "D",
    ]
    [project.optional-dependencies]
    docs = [
      "E",
    ]
    """
    expected = f"""\
    [project]
    keywords = [
    {" " * indent}"A",
    ]
    classifiers = [
    {" " * indent}"C",
    {" " * indent}"Programming Language :: Python :: 3 :: Only",
    {" " * indent}"Programming Language :: Python :: 3.8",
    {" " * indent}"Programming Language :: Python :: 3.9",
    {" " * indent}"Programming Language :: Python :: 3.10",
    {" " * indent}"Programming Language :: Python :: 3.11",
    {" " * indent}"Programming Language :: Python :: 3.12",
    ]
    dynamic = [
    {" " * indent}"B",
    ]
    dependencies = [
    {" " * indent}"d",
    ]
    [project.optional-dependencies]
    docs = [
    {" " * indent}"E",
    ]
    """
    fmt(txt, expected, indent=indent, keep_full_version=True)


def test_keep_full_version_on(fmt: Fmt) -> None:
    txt = """
    [project]
    dependencies = [
      "A==1.0.0",
    ]
    [project.optional-dependencies]
    docs = [
      "B==2.0.0",
    ]
    """
    expected = """\
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "a==1.0.0",
    ]
    [project.optional-dependencies]
    docs = [
      "B==2.0.0",
    ]
    """
    fmt(txt, expected, indent=2, keep_full_version=True, max_supported_python=(3, 8))


def test_keep_full_version_off(fmt: Fmt) -> None:
    txt = """
    [project]
    dependencies = [
      "A==1.0.0",
    ]
    [project.optional-dependencies]
    docs = [
      "B==2.0.0",
    ]
    """
    expected = """\
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "a==1",
    ]
    [project.optional-dependencies]
    docs = [
      "B==2",
    ]
    """
    fmt(txt, expected, indent=2, keep_full_version=False, max_supported_python=(3, 8))


def test_pyproject_toml_config(fmt: Fmt) -> None:
    txt = """
    [project]
    keywords = [
      "A",
    ]
    requires-python=">=3.8"
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
    indent = 4
    keep_full_version = false
    max_supported_python = "3.10"
    """
    expected = """\
    [project]
    keywords = [
        "A",
    ]
    requires-python=">=3.8"
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
        "requests>=2",
    ]

    [tool.pyproject-fmt]
    indent = 4
    keep_full_version = false
    max_supported_python = "3.10"
    """
    fmt(txt, expected, indent=6, keep_full_version=True, max_supported_python=(3, 10))

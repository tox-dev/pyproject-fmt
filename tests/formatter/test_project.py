from __future__ import annotations

from pathlib import Path
from subprocess import CalledProcessError
from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from pyproject_fmt.formatter.config import Config
from pyproject_fmt.formatter.project import fmt_project

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

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
    expected = """
    [project]
    classifiers = [
      "License :: OSI Approved :: MIT License",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, expected)


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


def test_classifier_none(fmt: Fmt) -> None:
    start = """
    [project]
    """
    fmt(fmt_project, start, start)


def test_classifier_lt(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<3.7"
    """
    expected = """
    [project]
    requires-python = "<3.7"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_gt(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = ">3.6"
    """
    expected = """
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
    fmt(fmt_project, start, expected)


def test_classifier_gte(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = ">=3.6"
    """
    expected = """
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
    fmt(fmt_project, start, expected)


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
    expected = """
    [project]
    requires-python="==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_neq(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "!=3.9"
    """
    expected = """
    [project]
    requires-python = "!=3.9"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_range(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python=">=3.7,<3.13"
    """
    expected = """
    [project]
    requires-python=">=3.7,<3.13"
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
    fmt(fmt_project, start, expected)


def test_classifier_range_neq(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<=3.12,!=3.9,>=3.8"
    """
    expected = """
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
    fmt(fmt_project, start, expected)


def test_classifier_high_range(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<=3.13,>3.10"
    """
    expected = """
    [project]
    requires-python = "<=3.13,>3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
      "Programming Language :: Python :: 3.13",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_upper_bound(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<3.8"
    classifiers = [
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
    ]
    """
    expected = """
    [project]
    requires-python = "<3.8"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_two_upper_bounds(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python = "<3.8,<=3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
    ]
    """
    expected = """
    [project]
    requires-python = "<3.8,<=3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_gt_tox(fmt: Fmt, tmp_path: Path) -> None:
    (tmp_path / "tox.ini").write_text("[tox]\nenv_list = py{311,312}-{magic}")
    start = """
    [project]
    requires-python=">=3.11"
    """
    expected = """
    [project]
    requires-python=">=3.11"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_gt_tox_no_py_ver(fmt: Fmt, tmp_path: Path) -> None:
    (tmp_path / "tox.ini").write_text("[tox]\nenv_list = py-{magic,p12}")
    start = """
    [project]
    requires-python=">=3.11"
    """
    expected = """
    [project]
    requires-python=">=3.11"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_gt_tox_conf_missing(fmt: Fmt) -> None:
    start = """
    [project]
    requires-python=">=3.12"
    """
    expected = """
    [project]
    requires-python=">=3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, expected)


def test_classifier_tox_fails_call(fmt: Fmt, mocker: MockerFixture) -> None:
    mocker.patch(
        "pyproject_fmt.formatter.project.check_output",
        side_effect=CalledProcessError(1, []),
    )

    start = """
    [project]
    requires-python=">=3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, start)


def test_classifier_tox_exe_bad(
    fmt: Fmt,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    tox_bin = tmp_path / "tox"
    tox_bin.write_text("")
    tox_bin.chmod(0o755)

    start = """
    [project]
    requires-python=">=3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    """
    fmt(fmt_project, start, start)


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
    expected = f"""
    [project]
    keywords = [
    {" " * indent}"A",
    ]
    classifiers = [
    {" " * indent}"C",
    ]
    dynamic = [
    {" " * indent}"B",
    ]
    dependencies = [
    {" " * indent}"D",
    ]
    [project.optional-dependencies]
    docs = [
    {" " * indent}"E",
    ]
    """
    config = Config(pyproject_toml=Path(), toml=dedent(txt), indent=indent)
    fmt(fmt_project, config, expected)


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
    config = Config(pyproject_toml=Path(), toml=dedent(txt), indent=2, keep_full_version=True)
    fmt(fmt_project, config, txt)


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
    expected = """
    [project]
    dependencies = [
      "A==1",
    ]
    [project.optional-dependencies]
    docs = [
      "B==2",
    ]
    """
    config = Config(pyproject_toml=Path(), toml=dedent(txt), indent=2, keep_full_version=False)
    fmt(fmt_project, config, expected)

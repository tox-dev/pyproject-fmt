from __future__ import annotations

from textwrap import dedent
from typing import TYPE_CHECKING

import pytest

from pyproject_fmt._pep508 import normalize_req

if TYPE_CHECKING:
    from tests import Fmt


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("a", "a"),
        ('packaging>=20.0;python_version>"3.4"', 'packaging>=20; python_version > "3.4"'),
        (
            "xonsh>=0.9.16;python_version>'3.4' and python_version!='3.9'",
            'xonsh>=0.9.16; python_version > "3.4" and python_version != "3.9"',
        ),
        ("pytest-xdist>=1.31.0", "pytest-xdist>=1.31"),
        ("foo@http://foo.com", "foo@ http://foo.com"),
        (
            "bar [fred,al] @ http://bat.com ;python_version=='2.7'",
            'bar[al,fred]@ http://bat.com ; python_version == "2.7"',
        ),
        (
            "baz [quux, strange];python_version<\"2.7\" and platform_version=='2'",
            'baz[quux,strange]; python_version < "2.7" and platform_version == "2"',
        ),
        ("pytest>=6.0.0", "pytest>=6"),
        ("pytest==6.0.0", "pytest==6"),
        ("pytest~=6.0.0", "pytest~=6.0.0"),
        ("a.b.c==6.0.0", "a-b-c==6"),
    ],
)
def test_requires_fmt(value: str, result: str) -> None:
    outcome = normalize_req(req=value, keep_full_version=False)
    assert outcome == result


@pytest.mark.parametrize("char", ["!", "=", ">", "<", " ", "\t", "@"])
def test_bad_syntax_requires(char: str) -> None:
    with pytest.raises(ValueError, match=f"[{char}]" if char.strip() else None):
        normalize_req(f"{char};", keep_full_version=False)


@pytest.mark.parametrize(
    ("value", "result"),
    [
        pytest.param("pytest==6.0.0", "pytest==6.0.0", id="major-minor-patch"),
        pytest.param("pytest==6.0", "pytest==6.0", id="major-minor"),
        pytest.param("pytest==6", "pytest==6", id="major"),
    ],
)
def test_requires_fmt_keep_full_version(value: str, result: str) -> None:
    outcome = normalize_req(req=value, keep_full_version=True)
    assert outcome == result


@pytest.mark.parametrize("indent", [0, 2, 4])
def test_normalize_pep508_array(fmt: Fmt, indent: int) -> None:
    start = """
        [project]
        dependencies = [
            "zzz>=1.1.1",
            "pytest==6.0.0",
        ]
        """
    expected = dedent(
        f"""\
        [project]
        dependencies = [
        {" " * indent}"pytest==6",
        {" " * indent}"zzz>=1.1.1",
        ]
        """,
    )
    fmt(start, expected, indent=indent, keep_full_version=False)

from __future__ import annotations

from textwrap import dedent
from typing import cast

import pytest
from tomlkit import parse
from tomlkit.items import Array

from pyproject_fmt.formatter.pep508 import normalize_pep508_array, normalize_req


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
    ],
)
def test_requires_fmt(value: str, result: str) -> None:
    outcome = normalize_req(req=value)
    assert outcome == result


@pytest.mark.parametrize("char", ["!", "=", ">", "<", " ", "\t", "@"])
def test_bad_syntax_requires(char: str) -> None:
    with pytest.raises(ValueError, match=f"[{char}]" if char.strip() else None):
        normalize_req(f"{char};")


@pytest.mark.parametrize("indent", [0, 2, 4])
def test_normalize_pep508_array(indent: int) -> None:
    toml_document_string = """
        requirements = [
            "zzz>=1.1.1",
            "pytest==6.0.0",
        ]
        """
    parsed = parse(toml_document_string)
    dependencies = parsed["requirements"]
    normalize_pep508_array(
        requires_array=cast(Array, dependencies),
        indent=indent,
        keep_full_version=False,
    )
    assert dependencies == ["zzz>=1.1.1", "pytest==6"]
    expected_string = dedent(
        f"""\
        [
        {" " * indent}"pytest==6",
        {" " * indent}"zzz>=1.1.1",
        ]
        """,
    ).strip()
    assert dependencies.as_string() == expected_string


def test_normalize_pep508_array_keep_versions() -> None:
    toml_document_string = """
        requirements = [
            "pytest==6.0.0",
        ]
        """
    parsed = parse(toml_document_string)
    dependencies = parsed["requirements"]
    normalize_pep508_array(
        requires_array=cast(Array, dependencies),
        indent=2,
        keep_full_version=True,
    )
    assert dependencies == ["pytest==6.0.0"]

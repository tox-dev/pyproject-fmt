from __future__ import annotations

from textwrap import dedent
from typing import cast

import pytest
from tomlkit import parse
from tomlkit.items import Array

from pyproject_fmt.formatter.pep508 import normalize_pep508_array, normalize_req, normalize_requires


@pytest.mark.parametrize(
    ("value", "result"),
    [
        ("", []),
        ("\t", []),
        ("\n\t\n", []),
        ("b\na\n", ["a", "b"]),
        ("a\nb\n", ["a", "b"]),
        ("A\na\n", ["A", "a"]),
        ("\nA\n\n\nb\n\n", ["A", "b"]),
        (
            'packaging>=20.0;python_version>"3.4"\n'
            "xonsh>=0.9.16;python_version > '3.4' and python_version != '3.9'\n"
            "pytest-xdist>=1.31.0\n"
            "foo@http://foo.com\n"
            "bar [fred,al] @ http://bat.com ;python_version=='2.7'\n"
            "baz [quux, strange];python_version<\"2.7\" and platform_version=='2'\n",
            [
                "foo@ http://foo.com",
                "pytest-xdist>=1.31",
                'bar[al,fred]@ http://bat.com ; python_version == "2.7"',
                'baz[quux,strange]; python_version < "2.7" and platform_version == "2"',
                'packaging>=20; python_version > "3.4"',
                'xonsh>=0.9.16; python_version > "3.4" and python_version != "3.9"',
            ],
        ),
        ("pytest>=6.0.0", ["pytest>=6"]),
        ("pytest==6.0.0", ["pytest==6"]),
        ("pytest~=6.0.0", ["pytest~=6.0.0"]),
    ],
)
def test_requires_fmt(value: str, result: list[str]) -> None:
    outcome = normalize_requires([i.strip() for i in value.splitlines() if i.strip()])
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
    normalize_pep508_array(requires_array=cast(Array, dependencies), indent=indent)
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

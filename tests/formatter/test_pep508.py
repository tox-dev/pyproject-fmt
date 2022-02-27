from __future__ import annotations

import pytest

from pyproject_fmt.formatter.pep508 import normalize_req, normalize_requires


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

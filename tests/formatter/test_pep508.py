from __future__ import annotations

import pytest
from packaging.requirements import Requirement

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
            "pytest-xdist>=1.31.0\n",
            [
                "pytest-xdist>=1.31",
                'packaging>=20;python_version>"3.4"',
                "xonsh>=0.9.16;python_version > '3.4' and python_version != '3.9'",
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


@pytest.mark.parametrize(
    "requirement",
    # Examples taken from or inspired by PEP 508
    [
        "A",
        "A.B-C_D",
        "aa",
        "name",
        "name<=1",
        "name>=3",
        "name>=3,<2",
        "name@http://foo.com",
        "name [fred,bar] @ http://foo.com ; python_version=='2.7'",
        "name[quux, strange];python_version<'2.7' and platform_version=='2'",
        "name; os_name=='a' or os_name=='b'",
        # Should parse as (a and b) or c
        "name; os_name=='a' and os_name=='b' or os_name=='c'",
        # Overriding precedence -> a and (b or c)
        "name; os_name=='a' and (os_name=='b' or os_name=='c')",
        # should parse as a or (b and c)
        "name; os_name=='a' or os_name=='b' and os_name=='c'",
        # Overriding precedence -> (a or b) and c
        "name; (os_name=='a' or os_name=='b') and os_name=='c'",
    ],
)
def test_format_dont_change_req_meaning(requirement):
    # Packaging.requirements.Requirement will parse the requirement string
    # using a proper grammar and then reconstruct it in a normalised way.
    original = Requirement(requirement)
    normalized = Requirement(normalize_req(requirement))
    # By comparing the pyproject-fmt and packaging normalisation we make sure
    # pyproject-fmt is not changing the underlying meaning/semantics of each
    # requirement.
    assert str(original) == str(normalized)

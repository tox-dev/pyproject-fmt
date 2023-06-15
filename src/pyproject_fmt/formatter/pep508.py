"""Apply package name normalization."""
from __future__ import annotations

from typing import TYPE_CHECKING

from packaging.requirements import Requirement
from tomlkit.api import string as toml_string

from .util import sorted_array

if TYPE_CHECKING:
    from tomlkit.items import Array, String


def normalize_req(req: str) -> str:
    """
    Normalize a python requirement.

    :param req: the raw requirement
    :return: normalized name
    """
    parsed = Requirement(req)
    for spec in parsed.specifier:
        if spec.operator in (">=", "=="):
            version = spec.version
            while version.endswith(".0"):
                version = version[:-2]
            spec._spec = (spec._spec[0], version)  # noqa: SLF001
    return str(parsed)


def normalize_requires(raws: list[str]) -> list[str]:
    """
    Normalize a list of requirements.

    :param raws: the raw values
    :return: the normalized values
    """
    return sorted(
        (normalize_req(req) for req in raws if req),
        key=lambda req: (";" in req, Requirement(req).name, req),
    )


def _best_effort_string_repr(req: str) -> String:
    # Convert requirement to a TOML string, choosing the most appropriate representation (basic or literal).
    # This function will attempt to use literal strings to avoid escaping double-quotes ("), if the requirement value
    # allows it, e.g. it does not contain other reserved characters such as single quotes (') or newlines (\\n).
    try:
        return toml_string(req, literal=('"' in req))
    except ValueError:
        return toml_string(req)


def normalize_pep508_array(requires_array: Array | None, indent: int) -> None:
    """
    Normalize a TOML array via PEP-508.

    :param requires_array: the input array
    :param indent: indentation level
    """
    if requires_array is None:
        return
    # first normalize values
    for at in range(len(requires_array)):
        normalized = _best_effort_string_repr(normalize_req(str(requires_array[at])))
        requires_array[at] = normalized
    # then sort
    sorted_array(requires_array, indent, key=lambda e: Requirement(e.text).name.lower())


__all__ = [
    "normalize_requires",
    "normalize_req",
    "normalize_pep508_array",
]

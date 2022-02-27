from __future__ import annotations

from packaging.requirements import Requirement
from tomlkit.api import string as toml_string
from tomlkit.items import Array, String

from .util import sorted_array


def normalize_req(req: str) -> str:
    parsed = Requirement(req)
    for spec in parsed.specifier:
        if spec.operator in (">=", "=="):
            version = spec.version
            while version.endswith(".0"):
                version = version[:-2]
            spec._spec = (spec._spec[0], version)
    return str(parsed)


def normalize_requires(raws: list[str]) -> list[str]:
    values = (normalize_req(req) for req in raws if req)
    normalized = sorted(values, key=lambda req: (";" in req, Requirement(req).name, req))
    return normalized


def _best_effort_string_repr(req: str) -> String:
    # Convert requirement to a TOML string, choosing the most appropriate representation (basic or literal).
    # This function will attempt to use literal strings to avoid escaping double-quotes ("), if the requirement value
    # allows it, e.g. it does not contain other reserved characters such as single quotes (') or newlines (\\n).
    try:
        return toml_string(req, literal=('"' in req))
    except ValueError:
        return toml_string(req)


def normalize_pep508_array(requires_array: Array | None, indent: int) -> None:
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

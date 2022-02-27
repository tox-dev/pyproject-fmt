from __future__ import annotations

import re

from packaging.requirements import Requirement
from tomlkit.api import string as toml_string
from tomlkit.items import Array, String

from .util import ArrayEntries, sorted_array

BASE_NAME_REGEX = re.compile(r"[^!=><~\s@]+")
REQ_REGEX = re.compile(r"(===|==|!=|~=|>=?|<=?|@)\s*([^,]+)")


def _req_base(lib: str) -> str:
    match = re.match(BASE_NAME_REGEX, lib)
    if match is None:
        raise ValueError(repr(lib))
    return match.group(0)


def _normalize_lib(lib: str) -> str:
    base = _req_base(lib)
    values = sorted(
        (f"{m.group(1)}{m.group(2)}" for m in REQ_REGEX.finditer(lib)), key=lambda c: ("<" in c, ">" in "c", c)
    )
    if values:  # strip .0 version
        while values[0].endswith(".0") and (values[0].startswith(">=") or values[0].startswith("==")):
            values[0] = values[0][:-2]
    return f"{base}{','.join(values)}"


def normalize_req(req: str) -> str:
    lib, sep, envs = req.partition(";")
    normalized = _normalize_lib(lib)
    return str(Requirement(f"{normalized}{sep}{envs}"))


def normalize_requires(raws: list[str]) -> list[str]:
    values = (normalize_req(req) for req in raws if req)
    normalized = sorted(values, key=lambda req: (";" in req, _req_base(req), req))
    return normalized


def _get_pkg_name(entry: ArrayEntries) -> str:
    match = BASE_NAME_REGEX.match(entry.text)
    assert match is not None
    return match.group(0)


def _best_effort_string_repr(req: str) -> String:
    """
    Convert requirement to a TOML string, choosing the most appropriate
    representation (basic or literal).

    This function will attempt to use literal strings to avoid escaping
    double-quotes ("), if the requirement value allows it, e.g. it does not
    contain other reserved characters such as single quotes (') or newlines (\\n).

    This is similar to black's approach (if the string contains double quotes,
    black uses single quotes as delimiter).
    """
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
    sorted_array(requires_array, indent, key=_get_pkg_name)


__all__ = [
    "normalize_requires",
    "normalize_req",
    "normalize_pep508_array",
]

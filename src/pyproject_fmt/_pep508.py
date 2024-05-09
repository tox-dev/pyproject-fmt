"""Apply package name normalization."""

from __future__ import annotations

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def normalize_req(req: str, *, keep_full_version: bool) -> str:
    """
    Normalize a python requirement.

    :param req: the raw requirement
    :param keep_full_version: whether to preserve, and therefore not normalize, requirements
    :return: normalized name
    """
    parsed = Requirement(req)
    if not keep_full_version:
        for spec in parsed.specifier:
            if spec.operator in {">=", "=="}:
                version = spec.version
                while version.endswith(".0"):
                    version = version[:-2]
                spec._spec = (spec._spec[0], version)  # noqa: SLF001
    parsed.name = canonicalize_name(parsed.name)
    return str(parsed)


def req_name(req: str) -> str:
    """
    Normalize a python requirement name.

    :param req: the raw requirement
    :return: normalized name
    """
    return canonicalize_name(Requirement(req).name)


__all__ = [
    "normalize_req",
]

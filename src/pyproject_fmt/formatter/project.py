"""Format the project table."""
from __future__ import annotations

import re
from shutil import which
from subprocess import CalledProcessError, check_output
from typing import TYPE_CHECKING, Optional, cast

from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import Version
from tomlkit.items import Array, String, Table, Trivia

from .pep508 import normalize_pep508_array
from .util import ensure_newline_at_end, order_keys, sorted_array

if TYPE_CHECKING:
    from tomlkit.toml_document import TOMLDocument

    from .config import Config

_PY_MIN_VERSION: int = 7
_PY_MAX_VERSION: int = 12


def fmt_project(parsed: TOMLDocument, conf: Config) -> None:  # noqa: C901
    """
    Format the project table.

    :param parsed: the raw parsed table
    :param conf: configuration
    """
    project = cast(Optional[Table], parsed.get("project"))
    if project is None:
        return

    if "name" in project:  # normalize names to hyphen so sdist / wheel have the same prefix
        name = project["name"]
        assert isinstance(name, str)  # noqa: S101
        project["name"] = canonicalize_name(name)
    if "description" in project:
        project["description"] = String.from_raw(str(project["description"]).strip())

    sorted_array(cast(Optional[Array], project.get("keywords")), indent=conf.indent)
    sorted_array(cast(Optional[Array], project.get("dynamic")), indent=conf.indent)

    if "requires-python" in project:
        _add_py_classifiers(project)

    sorted_array(cast(Optional[Array], project.get("classifiers")), indent=conf.indent, custom_sort="natsort")

    normalize_pep508_array(
        requires_array=cast(Optional[Array], project.get("dependencies")),
        indent=conf.indent,
        keep_full_version=conf.keep_full_version,
    )
    if "optional-dependencies" in project:
        opt_deps = cast(Table, project["optional-dependencies"])
        for value in opt_deps.values():
            normalize_pep508_array(
                requires_array=cast(Array, value),
                indent=conf.indent,
                keep_full_version=conf.keep_full_version,
            )
        order_keys(opt_deps, (), sort_key=lambda k: k[0])  # pragma: no branch

    for of_type in ("scripts", "gui-scripts", "entry-points", "urls"):
        if of_type in project:
            table = cast(Table, project[of_type])
            order_keys(table, (), sort_key=lambda k: k[0])  # pragma: no branch

    if "entry-points" in project:  # order entry points sub-table
        entry_points = cast(Table, project["entry-points"])
        order_keys(entry_points, (), sort_key=lambda k: k[0])  # pragma: no branch
        for entry_point in entry_points.values():
            order_keys(entry_point, (), sort_key=lambda k: k[0])  # pragma: no branch

    # order maintainers and authors table
    # handle readme table

    key_order = [
        "name",
        "version",
        "description",
        "readme",
        "keywords",
        "license",
        "license-files",
    ]
    key_order.extend(
        [
            "maintainers",
            "authors",
            "requires-python",
            "classifiers",
            "dynamic",
            "dependencies",
        ],
    )
    # these go at the end as they may be inline or exploded
    key_order.extend(
        ["optional-dependencies", "urls", "scripts", "gui-scripts", "entry-points"],
    )
    order_keys(project, key_order)
    ensure_newline_at_end(project)


def _add_py_classifiers(project: Table) -> None:
    specifiers = SpecifierSet(project.get("requires-python", f">=3.{_PY_MIN_VERSION}"))

    min_version = _get_min_version_classifier(specifiers)
    max_version = _get_max_version_classifier(specifiers)

    allowed_versions = list(specifiers.filter(f"3.{v}" for v in range(min_version, max_version + 1)))

    add = [f"Programming Language :: Python :: {v}" for v in allowed_versions]
    add.append("Programming Language :: Python :: 3 :: Only")

    if "classifiers" in project:
        classifiers: Array = cast(Array, project["classifiers"])
    else:
        classifiers = Array([], Trivia(), multiline=False)
        project["classifiers"] = classifiers

    exist = set(classifiers.unwrap())
    remove = [e for e in exist if re.fullmatch(r"Programming Language :: Python :: \d.*", e) and e not in add]
    deleted = 0
    for at, item in enumerate(list(classifiers)):
        if item in remove:
            del classifiers[at - deleted]
            deleted += 1

    for entry in add:
        if entry not in classifiers:
            classifiers.insert(len(add), entry)


def _get_min_version_classifier(specifiers: SpecifierSet) -> int:
    min_version: list[int] = []
    for specifier in specifiers:
        if specifier.operator == ">=":
            min_version.append(Version(specifier.version).minor)
        if specifier.operator == ">":
            min_version.append(Version(specifier.version).minor + 1)
    return min(min_version) if min_version else _PY_MIN_VERSION


def _get_max_version_classifier(specifiers: SpecifierSet) -> int:
    max_version: list[int] = []

    for specifier in specifiers:
        if specifier.operator == "<=":
            max_version.append(Version(specifier.version).minor)
        if specifier.operator == "<":
            max_version.append(Version(specifier.version).minor - 1)
    return max(max_version) if max_version else (_get_max_version_tox() or _PY_MAX_VERSION)


def _get_max_version_tox() -> int | None:
    tox = which("tox")
    if tox is not None:  # pragma: no branch
        try:
            tox_environments = check_output([tox, "-aqq"], encoding="utf-8", text=True)  # noqa: S603
        except (OSError, CalledProcessError):
            tox_environments = ""
        if not re.match(r"ROOT: No .* found, assuming empty", tox_environments):
            found = set()
            for env in tox_environments.split():
                for part in env.split("-"):
                    match = re.match(r"py(\d)(\d+)", part)
                    if match:
                        found.add(int(match.groups()[1]))
            if found:
                return max(found)
    return None


__all__ = [
    "fmt_project",
]

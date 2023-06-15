"""Format the project table."""
from __future__ import annotations

import re
import subprocess
from shutil import which
from typing import TYPE_CHECKING, Optional, cast

from packaging.utils import canonicalize_name
from tomlkit.items import Array, String, Table, Trivia

from .pep508 import normalize_pep508_array
from .util import ensure_newline_at_end, order_keys, sorted_array

if TYPE_CHECKING:
    from tomlkit.toml_document import TOMLDocument

    from .config import Config

_PY_MIN_VERSION: int = 7
_PY_MAX_VERSION: int = 11


def _get_max_version() -> int:
    max_version = _PY_MAX_VERSION
    tox = which("tox")
    if tox is not None:  # pragma: no branch
        tox_environments = subprocess.check_output(
            ["tox", "-aqq"],  # noqa: S603, S607
            encoding="utf-8",
            text=True,
        )
        if not re.match(r"ROOT: No .* found, assuming empty", tox_environments):
            found = set()
            for env in tox_environments.split():
                for part in env.split("-"):
                    match = re.match(r"py(\d)(\d+)", part)
                    if match:
                        found.add(int(match.groups()[1]))
            if found:
                max_version = max(found)
    return max_version


def _add_py_classifiers(project: Table) -> None:
    # update classifiers depending on requires
    requires = project.get("requires-python", f">=3.{_PY_MIN_VERSION}")
    if not (requires.startswith(("==", ">="))):
        return
    versions = [int(i) for i in requires[2:].split(".")[:2]]
    major, minor = versions[0], versions[1] if len(versions) > 1 else _PY_MIN_VERSION
    if requires.startswith(">="):
        supports = [(major, i) for i in range(minor, _get_max_version() + 1)]
    else:
        supports = [(major, minor)]
    add = [f"Programming Language :: Python :: {ma}.{mi}" for (ma, mi) in supports]
    if requires.startswith(">="):
        add.append("Programming Language :: Python :: 3 :: Only")
    if "classifiers" in project:
        classifiers: Array = cast(Array, project["classifiers"])
    else:
        classifiers = Array([], Trivia(), multiline=False)
        project["classifiers"] = classifiers

    exist = set(classifiers.unwrap())
    remove = [
        e
        for e in exist
        if re.fullmatch(r"Programming Language :: Python :: \d.*", e) and e not in add
    ]
    deleted = 0
    for at, item in enumerate(list(classifiers)):
        if item in remove:
            del classifiers[at - deleted]
            deleted += 1

    for entry in add:
        if entry not in classifiers:
            classifiers.insert(len(add), entry)


def fmt_project(parsed: TOMLDocument, conf: Config) -> None:  # noqa: C901
    """
    Format the project table.

    :param parsed: the raw parsed table
    :param conf: configuration
    """
    project = cast(Optional[Table], parsed.get("project"))
    if project is None:
        return

    if (
        "name" in project
    ):  # normalize names to hyphen so sdist / wheel have the same prefix
        name = project["name"]
        assert isinstance(name, str)  # noqa: S101
        project["name"] = canonicalize_name(name)
    if "description" in project:
        project["description"] = String.from_raw(str(project["description"]).strip())

    sorted_array(cast(Optional[Array], project.get("keywords")), indent=conf.indent)
    sorted_array(cast(Optional[Array], project.get("dynamic")), indent=conf.indent)

    if "requires-python" in project:
        _add_py_classifiers(project)

    sorted_array(
        cast(Optional[Array], project.get("classifiers")),
        indent=conf.indent,
        custom_sort="natsort",
    )

    normalize_pep508_array(
        cast(Optional[Array], project.get("dependencies")),
        conf.indent,
    )
    if "optional-dependencies" in project:
        opt_deps = cast(Table, project["optional-dependencies"])
        for value in opt_deps.values():
            normalize_pep508_array(cast(Array, value), conf.indent)
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


__all__ = [
    "fmt_project",
]

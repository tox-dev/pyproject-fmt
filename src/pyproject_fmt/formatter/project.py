from __future__ import annotations

from typing import Optional, cast

from tomlkit.items import Array, String, Table
from tomlkit.toml_document import TOMLDocument

from .config import Config
from .pep508 import normalize_pep508_array
from .util import order_keys, sorted_array


def fmt_project(parsed: TOMLDocument, conf: Config) -> None:
    project = cast(Optional[Table], parsed.get("project"))
    if project is None:
        return

    if "name" in project:  # normalize names to underscore so sdist / wheel have the same prefix
        name = project["name"]
        assert isinstance(name, str)
        project["name"] = name.replace("-", "_")
    if "description" in project:
        project["description"] = String.from_raw(str(project["description"]).strip())

    sorted_array(cast(Optional[Array], project.get("keywords")), indent=conf.indent)
    sorted_array(cast(Optional[Array], project.get("dynamic")), indent=conf.indent)

    normalize_pep508_array(cast(Optional[Array], project.get("dependencies")), conf.indent)
    if "optional-dependencies" in project:
        opt_deps = cast(Table, project["optional-dependencies"])
        for value in opt_deps.values():
            normalize_pep508_array(cast(Array, value), conf.indent)
        order_keys(opt_deps.value.body, (), sort_key=lambda k: k[0])

    for of_type in ("scripts", "gui-scripts", "entry-points", "urls"):
        if of_type in project:
            table = cast(Table, project[of_type])
            order_keys(table.value.body, (), sort_key=lambda k: k[0])

    if "entry-points" in project:  # order entry points sub-table
        entry_points = cast(Table, project["entry-points"])
        order_keys(entry_points.value.body, (), sort_key=lambda k: k[0])
        for entry_point in entry_points.values():
            order_keys(entry_point.value.body, (), sort_key=lambda k: k[0])

    # license: Optional[Union[str, LicenseTableLegacy]]
    # license_files: Optional[LicenseFilesTable] = Field(alias="license-files")
    # readme: Optional[Union[str, ReadmeTable]]
    # order maintainers and authors table
    # update classifiers depending on requires
    # handle readme table

    order_keys(
        project.value.body,
        (
            "name",
            "version",
            "description",
            "readme",
            "keywords",
            "license",
            "license-files",
            "maintainers",
            "authors",
            "requires-python",
            "dependencies",
            "dynamic",
            "classifiers",
            "optional-dependencies",
            "urls",
            "scripts",
            "gui-scripts",
            "entry-points",
        ),
    )


__all__ = [
    "fmt_project",
]

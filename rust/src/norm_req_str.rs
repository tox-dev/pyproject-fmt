use pyo3::prelude::*;
use pyo3::types::IntoPyDict;
use taplo::parser::parse;
use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};

use crate::common::get_table_name;

pub fn normalize_requirements(root_ast: &mut SyntaxNode, keep_full_version: bool) {
    let mut table = String::new();
    for top_level_children in root_ast.children_with_tokens() {
        if top_level_children.kind() == SyntaxKind::TABLE_HEADER {
            table = get_table_name(&top_level_children);
        } else if top_level_children.kind() == SyntaxKind::ENTRY && ["build-system", "project"].contains(&&*table) {
            let mut key = String::new();
            for table_entry in top_level_children.as_node().unwrap().children_with_tokens() {
                if table_entry.kind() == SyntaxKind::KEY {
                    key = table_entry.as_node().unwrap().text().to_string().trim().to_string();
                } else if table_entry.kind() == SyntaxKind::VALUE
                    && ((table == "build-system" && key == "requires") || (table == "project" && key == "dependencies"))
                {
                    for table_value in table_entry.as_node().unwrap().children_with_tokens() {
                        if table_value.kind() == SyntaxKind::ARRAY {
                            normalize_array(table_value, keep_full_version);
                        }
                    }
                }
            }
        }
    }
}

fn normalize_array(table_value: SyntaxElement, keep_full_version: bool) {
    for entry in table_value.as_node().unwrap().children_with_tokens() {
        if entry.kind() == SyntaxKind::VALUE {
            let mut to_insert = Vec::<SyntaxElement>::new();
            let node = entry.as_node().unwrap();
            for element in node.children_with_tokens() {
                if element.kind() == SyntaxKind::STRING {
                    let found = entry.as_node().unwrap().text().to_string();
                    let found_str_value = &found[1..found.len() - 1];
                    let new_str_value = normalize_req_str(found_str_value, keep_full_version);
                    if found_str_value != new_str_value {
                        to_insert.push(create_string_node(element, new_str_value));
                    } else {
                        to_insert.push(element);
                    }
                } else {
                    to_insert.push(element);
                }
            }
            node.splice_children(0..to_insert.len(), to_insert);
        }
    }
}

fn normalize_req_str(value: &str, keep_full_version: bool) -> String {
    Python::with_gil(|py| {
        let norm: String = PyModule::import_bound(py, "pyproject_fmt._pep508")?
            .getattr("normalize_req")?
            .call(
                (value,),
                Some(&[("keep_full_version", keep_full_version)].into_py_dict_bound(py)),
            )?
            .extract()?;
        Ok::<String, PyErr>(norm)
    })
    .unwrap()
}

fn create_string_node(element: SyntaxElement, text: String) -> SyntaxElement {
    for root in parse(&format!("a = \"{}\"", text))
        .into_syntax()
        .clone_for_update()
        .first_child()
        .unwrap()
        .children_with_tokens()
    {
        if root.kind() == SyntaxKind::VALUE {
            for entries in root.as_node().unwrap().children_with_tokens() {
                if entries.kind() == SyntaxKind::STRING {
                    return entries;
                }
            }
        }
    }
    element
}

#[cfg(test)]
mod tests {
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;

    use crate::norm_req_str::normalize_requirements;

    fn evaluate(start: String, keep_full_version: bool) -> String {
        let mut root_ast = parse(&start).into_syntax().clone_for_update();
        normalize_requirements(&mut root_ast, keep_full_version);
        format_syntax(root_ast, Options::default())
    }

    #[rstest]
    #[case(
    r#"
# magic file

[ build-system ]
build-backend = "hatchling.build"
requires = [
  "hatch-vcs>=0.4",
  "hatchling>=1.18",
]
[project]
name = "pyproject-fmt"
description = "Format your pyproject.toml file"
readme = "README.md"
keywords = [
  "format",
  "pyproject",
]
license.file = "LICENSE.txt"
authors = [
  { name = "Bernat Gabor", email = "gaborjbernat@gmail.com" },
]
requires-python = ">=3.8"
classifiers = [
  "License :: OSI Approved :: MIT License",
  "Operating System :: OS Independent",
  "Programming Language :: Python :: 3 :: Only",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.8",
  "Programming Language :: Python :: 3.9",
  "Programming Language :: Python",
]
dynamic = [
  "version",
]
dependencies = [
  "natsort>=8.4",
  "packaging>=23.2",
  "tomlkit>=0.12.3",
]
optional-dependencies.docs = [
  "furo>=2023.9.10",
  "sphinx-argparse-cli>=1.11.1",
  "sphinx-autodoc-typehints>=1.25.2",
  "sphinx-copybutton>=0.5.2",
  "sphinx>=7.2.6",
]
optional-dependencies.test = [
  "covdefaults>=2.3",
  "pytest-cov>=4.1",
  "pytest-mock>=3.12",
  "pytest>=7.4.3",
]
urls."Bug Tracker" = "https://github.com/tox-dev/pyproject-fmt/issues"
urls."Changelog" = "https://github.com/tox-dev/pyproject-fmt/releases"
urls.Documentation = "https://github.com/tox-dev/pyproject-fmt/"
urls."Source Code" = "https://github.com/tox-dev/pyproject-fmt"
scripts.pyproject-fmt = "pyproject_fmt.__main__:run"

[tool.hatch]
build.dev-mode-dirs = [
  "src",
]
build.hooks.vcs.version-file = "src/pyproject_fmt/_version.py"
build.targets.sdist.include = [
  "/src",
  "/tests",
  "tox.ini",
]
version.source = "vcs"

[tool.ruff]
line-length = 120
target-version = "py38"
lint.isort = { known-first-party = [
  "pyproject_fmt",
], required-imports = [
  "from __future__ import annotations",
] }
lint.select = [
  "ALL",
]
lint.ignore = [
  "ANN101", # no type annotation for self
  "ANN401", # allow Any as type annotation
  "COM812", # Conflict with formatter
  "CPY",    # No copyright statements
  "D203",   # `one-blank-line-before-class` (D203) and `no-blank-line-before-class` (D211) are incompatible
  "D212",   # `multi-line-summary-first-line` (D212) and `multi-line-summary-second-line` (D213) are incompatible
  "ISC001", # Conflict with formatter
  "S104",   # Possible binding to all interface
]
lint.preview = true
format.preview = true
format.docstring-code-format = true
format.docstring-code-line-length = 100

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
  "D",       # don"t care about documentation in tests
  "FBT",     # don"t care about booleans as positional arguments in tests
  "INP001",  # no implicit namespace
  "PLC2701", # private import
  "PLR0913", # any number of arguments in tests
  "PLR0917", # any number of arguments in tests
  "PLR2004", # Magic value used in comparison, consider replacing with a constant variable
  "S101",    # asserts allowed in tests...
  "S603",    # `subprocess` call: check for execution of untrusted input # magic  asd sad sa dsad sad sa asd asd sa dasd asd sad as
  # magic                                                                                       `
]

[tool.codespell]
builtin = "clear,usage,en-GB_to_en-US"
count = true
[tool.pytest]
ini_options.testpaths = [
  "tests",
]

[tool.coverage]
html.show_contexts = true
html.skip_covered = false
paths.source = [
  "*/src",
  ".tox/*/lib/python*/site-packages",
  "src",
]
report.fail_under = 88
run.parallel = true
run.plugins = [
  "covdefaults",
]

[tool.mypy]
show_error_codes = true
strict = true

    "#,
    true,
    r#"
    [build-system]
    requires=["maturin>=1.5"]
    "#
    )]
    fn test_normalize_requirement(#[case] start: String, #[case] keep_full_version: bool, #[case] expected: String) {
        assert_eq!(expected, evaluate(start, keep_full_version));
    }
}

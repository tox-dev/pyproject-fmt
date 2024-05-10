use std::string::String;

use pyo3::prelude::PyModule;
use pyo3::{pyfunction, pymodule, wrap_pyfunction, Bound, PyResult};
use taplo::formatter::{format_syntax, Options};
use taplo::parser::parse;

use crate::build_system::fix_build;
use crate::global::reorder_tables;
use crate::helpers::table::Tables;
use crate::project::fix_project_table;

mod build_system;
mod project;

mod global;
mod helpers;

/// Format toml file
#[pyfunction]
#[must_use]
pub fn format_toml(
    content: &str,
    column_width: usize,
    indent: usize,
    keep_full_version: bool,
    max_supported_python: (u8, u8),
    min_supported_python: (u8, u8),
) -> String {
    let root_ast = parse(content).into_syntax().clone_for_update();
    let mut tables = Tables::from_ast(&root_ast);

    fix_build(&mut tables, keep_full_version);
    fix_project_table(
        &mut tables,
        keep_full_version,
        max_supported_python,
        min_supported_python,
    );
    reorder_tables(&root_ast, &mut tables);

    let options = Options {
        align_entries: false,         // do not align by =
        align_comments: true,         // align inline comments
        align_single_comments: true,  // align comments after entries
        array_trailing_comma: true,   // ensure arrays finish with trailing comma
        array_auto_expand: true,      // arrays go to multi line for easier diffs
        array_auto_collapse: false,   // do not collapse for easier diffs
        compact_arrays: false,        // do not compact for easier diffs
        compact_inline_tables: false, // do not compact for easier diffs
        compact_entries: false,       // do not compact for easier diffs
        column_width,                 // always expand arrays per https://github.com/tamasfe/taplo/issues/390
        indent_tables: false,
        indent_entries: false,
        inline_table_expand: true,
        trailing_newline: true,
        allowed_blank_lines: 1, // one blank line to separate
        indent_string: " ".repeat(indent),
        reorder_keys: false,   // respect custom order
        reorder_arrays: false, // for natural sorting we need to this ourselves
        crlf: false,
    };
    format_syntax(root_ast, options)
}

/// # Errors
///
/// Will return `PyErr` if an error is raised during formatting.
#[pymodule]
#[pyo3(name = "_lib")]
#[cfg(not(tarpaulin_include))]
pub fn _lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(format_toml, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;

    use crate::format_toml;

    #[rstest]
    #[case::simple(
        indoc ! {r#"
    # comment
    a= "b"
    [project]
    name="alpha"
    dependencies=[" e >= 1.5.0"]
    [build-system]
    build-backend="backend"
    requires=[" c >= 1.5.0", "d == 2.0.0"]
    [tool.mypy]
    mk="mv"
    "#},
        indoc ! {r#"
    # comment
    a = "b"

    [build-system]
    build-backend = "backend"
    requires = [
      "c>=1.5",
      "d==2",
    ]

    [project]
    name = "alpha"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    dependencies = [
      "e>=1.5",
    ]

    [tool.mypy]
    mk = "mv"
    "#},
        2,
        false,
        (3, 12),
    )]
    #[case::empty(
        indoc ! {r""},
        "\n",
        2,
        true,
        (3, 12)
    )]
    #[case::scripts(
        indoc ! {r#"
    [project.scripts]
    c = "d"
    a = "b"
    "#},
        indoc ! {r#"
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    scripts.a = "b"
    scripts.c = "d"
    "#},
        2,
        true,
        (3, 8)
    )]
    fn test_format_toml(
        #[case] start: &str,
        #[case] expected: &str,
        #[case] indent: usize,
        #[case] keep_full_version: bool,
        #[case] max_supported_python: (u8, u8),
    ) {
        let got = format_toml(start, 1, indent, keep_full_version, max_supported_python, (3, 8));
        assert_eq!(got, expected);
    }
}

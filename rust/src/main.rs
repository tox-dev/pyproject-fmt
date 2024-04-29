use std::string::String;

use pyo3::prelude::PyModule;
use pyo3::{pyfunction, pymodule, wrap_pyfunction, Bound, PyResult};
use taplo::formatter::{format_syntax, Options};
use taplo::parser::parse;
use taplo::syntax::{SyntaxKind, SyntaxNode};

use crate::build_system::fix_build_system;
use crate::common::get_table_name;
use crate::project::fix_project;
use crate::table_ordering::reorder_table;

mod build_system;
mod common;
mod pep503;
mod project;
mod table_ordering;

/// Format toml file
#[pyfunction]
pub fn format_toml(content: String, indent: usize, keep_full_version: bool, max_supported_python: (u8, u8)) -> String {
    let mut root_ast = parse(&content).into_syntax().clone_for_update();
    reorder_table(&mut root_ast);
    fix_entries(&mut root_ast, keep_full_version, max_supported_python);

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
        column_width: 1,              // always expand arrays per https://github.com/tamasfe/taplo/issues/390
        indent_tables: false,
        indent_entries: false,
        inline_table_expand: true,
        trailing_newline: true,
        allowed_blank_lines: 1, // one blank line to separate
        indent_string: " ".repeat(indent),
        reorder_keys: false,  // respect custom order
        reorder_arrays: true, // stable order in arrays
        crlf: false,
    };
    format_syntax(root_ast, options)
}

fn fix_entries(root_ast: &mut SyntaxNode, keep_full_version: bool, max_supported_python: (u8, u8)) {
    let mut table_name = String::new();
    for children in root_ast.children_with_tokens() {
        if children.kind() == SyntaxKind::TABLE_HEADER {
            table_name = get_table_name(&children);
        } else if children.kind() == SyntaxKind::ENTRY {
            if table_name == "build-system" {
                fix_build_system(children, keep_full_version)
            } else if table_name == "project" {
                fix_project(children, keep_full_version, max_supported_python);
            }
        }
    }
}

#[pymodule]
#[pyo3(name = "_lib")]
#[cfg(not(tarpaulin_include))]
fn _lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(format_toml, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use pretty_assertions::assert_eq;
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
    fn test_format_toml(
        #[case] start: &str,
        #[case] expected: &str,
        #[case] indent: usize,
        #[case] keep_full_version: bool,
        #[case] max_supported_python: (u8, u8),
    ) {
        assert_eq!(
            expected,
            format_toml(start.parse().unwrap(), indent, keep_full_version, max_supported_python)
        );
    }
}

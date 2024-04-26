use std::string::String;

use pyo3::{Bound, pyfunction, pymodule, PyResult, wrap_pyfunction};
use pyo3::prelude::PyModule;
use taplo::formatter::{format_syntax, Options};
use taplo::parser::parse;

use crate::norm_req_str::normalize_requirements;
use crate::table_ordering::reorder_table;

mod common;
mod norm_req_str;
mod table_ordering;

/// Format toml file
#[pyfunction]
pub fn format_toml(content: String, indent: usize, keep_full_version: bool, max_supported_python: (u8, u8)) -> String {
    println!("max {:?}", max_supported_python);
    let mut root_ast = parse(&content).into_syntax().clone_for_update();
    reorder_table(&mut root_ast);
    normalize_requirements(&mut root_ast, keep_full_version);

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
    use rstest::rstest;

    use crate::format_toml;

    #[rstest]
    #[case::simple(
    indoc ! {r#"
    # comment
    a= "b"
    [build-system]
    requires=[" c >= 1.5.0", "d == 2.0.0"]
    [tool.mypy]
    mk="mv"
    [tool.ruff.test]
    mrt="vrt"
    [extra]
    ek = "ev"
    [tool.ruff]
    mr="vr"
    "#},
    indoc ! {r#"
    # comment
    a = "b"
    [build-system]
    requires = [
      "c>=1.5.0",
      "d==2.0.0",
    ]
    [extra]
    ek = "ev"
    [tool.ruff]
    mr = "vr"
    [tool.ruff.test]
    mrt = "vrt"
    [tool.mypy]
    mk = "mv"
    "#},
    2,
    true,
    (3, 12),
    )]
    fn test_normalize_requirement(#[case] start: &str, #[case] expected: &str, #[case] indent: usize, #[case] keep_full_version: bool, #[case] max_supported_python: (u8, u8)) {
        assert_eq!(expected, format_toml(start.parse().unwrap(), indent, keep_full_version, max_supported_python));
    }
}

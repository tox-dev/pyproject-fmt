use pyo3::prelude::*;
use pyo3::prepare_freethreaded_python;
use pyo3::types::IntoPyDict;
use taplo::syntax::{SyntaxElement, SyntaxKind};

use crate::common::create_string_node;

pub fn normalize_array(table_value: SyntaxElement, keep_full_version: bool) {
    for entry in table_value.as_node().unwrap().children_with_tokens() {
        if entry.kind() == SyntaxKind::VALUE {
            let mut to_insert = Vec::<SyntaxElement>::new();
            let node = entry.as_node().unwrap();
            for element in node.children_with_tokens() {
                if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&element.kind()) {
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
    prepare_freethreaded_python();
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

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use pretty_assertions::assert_eq;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;
    use taplo::syntax::SyntaxKind;

    use crate::pep503::normalize_array;

    fn evaluate(start: &str, keep_full_version: bool) -> String {
        let root_ast = parse(start).into_syntax().clone_for_update();
        for children in root_ast.children_with_tokens() {
            if children.kind() == SyntaxKind::ENTRY {
                for entry in children.as_node().unwrap().children_with_tokens() {
                    if entry.kind() == SyntaxKind::VALUE {
                        for array in entry.as_node().unwrap().children_with_tokens() {
                            if array.kind() == SyntaxKind::ARRAY {
                                normalize_array(array, keep_full_version);
                            }
                        }
                    }
                }
            }
        }
        format_syntax(root_ast, Options::default())
    }

    #[rstest]
    #[case::strip_micro_no_keep(
    indoc ! {r#"
    a=["maturin >= 1.5.0"]
    "#},
    indoc ! {r#"
    a = ["maturin>=1.5"]
    "#},
    false
    )]
    #[case::strip_micro_keep(
    indoc ! {r#"
    a=["maturin >= 1.5.0"]
    "#},
    indoc ! {r#"
    a = ["maturin>=1.5.0"]
    "#},
    true
    )]
    #[case::no_change(
    indoc ! {r#"
    a = [
    "maturin>=1.5.3",# comment here
    # a comment afterwards
    ]
    "#},
    indoc ! {r#"
    a = [
      "maturin>=1.5.3", # comment here
      # a comment afterwards
    ]
    "#},
    false
    )]
    #[case::ignore_non_string(
    indoc ! {r#"
    a=[{key="maturin>=1.5.0"}]
    "#},
    indoc ! {r#"
    a = [{ key = "maturin>=1.5.0" }]
    "#},
    false
    )]
    #[case::has_double_quote(
    indoc ! {r#"
    a=['importlib-metadata>=7.0.0;python_version<"3.8"']
    "#},
    indoc ! {r#"
    a = ["importlib-metadata>=7; python_version < \"3.8\""]
    "#},
    false
    )]
    fn test_normalize_requirement(#[case] start: &str, #[case] expected: &str, #[case] keep_full_version: bool) {
        assert_eq!(expected, evaluate(start, keep_full_version));
    }
}

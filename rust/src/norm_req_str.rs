use pyo3::prelude::*;
use pyo3::prepare_freethreaded_python;
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

fn create_string_node(element: SyntaxElement, text: String) -> SyntaxElement {
    let expr = &format!("a = \"{}\"", text.replace('"', "\\\""));
    for root in parse(expr)
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
    panic!("Could not create string element for {:?}", element)
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;

    use crate::norm_req_str::normalize_requirements;

    fn evaluate(start: &str, keep_full_version: bool) -> String {
        let mut root_ast = parse(start).into_syntax().clone_for_update();
        normalize_requirements(&mut root_ast, keep_full_version);
        format_syntax(root_ast, Options::default())
    }

    #[rstest]
    #[case::strip_micro_no_keep(
    indoc ! {r#"
    [build-system]
    requires=["maturin >= 1.5.0"]
    "#},
    indoc ! {r#"
    [build-system]
    requires = ["maturin>=1.5"]
    "#},
    false
    )]
    #[case::strip_micro_keep(
    indoc ! {r#"
    [build-system]
    requires=["maturin >= 1.5.0"]
    "#},
    indoc ! {r#"
    [build-system]
    requires = ["maturin>=1.5.0"]
    "#},
    true
    )]
    #[case::no_change(
    indoc ! {r#"
    [build-system]
    requires = [
    "maturin>=1.5.3",# comment here
    # a comment afterwards
    ]
    "#},
    indoc ! {r#"
    [build-system]
    requires = [
      "maturin>=1.5.3", # comment here
      # a comment afterwards
    ]
    "#},
    false
    )]
    #[case::ignore_non_string(
    indoc ! {r#"
    [build-system]
    requires=[{key="maturin>=1.5.0"}]
    "#},
    indoc ! {r#"
    [build-system]
    requires = [{ key = "maturin>=1.5.0" }]
    "#},
    false
    )]
    #[case::has_double_quote(
    indoc ! {r#"
    [project]
    dependencies=['importlib-metadata>=7.0.0;python_version<"3.8"']
    "#},
    indoc ! {r#"
    [project]
    dependencies = ["importlib-metadata>=7; python_version < \"3.8\""]
    "#},
    false
    )]
    fn test_normalize_requirement(#[case] start: &str, #[case] expected: &str, #[case] keep_full_version: bool) {
        assert_eq!(expected, evaluate(start, keep_full_version));
    }
}

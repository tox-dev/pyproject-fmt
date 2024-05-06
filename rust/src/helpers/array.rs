use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};

use crate::helpers::create::create_string_node;
use crate::helpers::pep508::normalize_req_str;

pub fn array_pep508_normalize(node: &SyntaxNode, keep_full_version: bool) {
    for array in node.children_with_tokens() {
        if array.kind() == SyntaxKind::ARRAY {
            for array_entry in array.as_node().unwrap().children_with_tokens() {
                if array_entry.kind() == SyntaxKind::VALUE {
                    let mut to_insert = Vec::<SyntaxElement>::new();
                    let value_node = array_entry.as_node().unwrap();
                    let mut changed = false;
                    for mut element in value_node.children_with_tokens() {
                        if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&element.kind()) {
                            let found = element.as_token().unwrap().text().to_string();
                            let found_str_value = &found[1..found.len() - 1];
                            let new_str_value = normalize_req_str(found_str_value, keep_full_version);
                            if found_str_value != new_str_value {
                                element = create_string_node(element, new_str_value);
                                changed = true;
                            }
                        }
                        to_insert.push(element);
                    }
                    if changed {
                        value_node.splice_children(0..to_insert.len(), to_insert);
                    }
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;
    use taplo::syntax::SyntaxKind;

    use crate::helpers::array::array_pep508_normalize;

    fn evaluate(start: &str, keep_full_version: bool) -> String {
        let root_ast = parse(start).into_syntax().clone_for_update();
        for children in root_ast.children_with_tokens() {
            if children.kind() == SyntaxKind::ENTRY {
                for entry in children.as_node().unwrap().children_with_tokens() {
                    if entry.kind() == SyntaxKind::VALUE {
                        array_pep508_normalize(entry.as_node().unwrap(), keep_full_version);
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

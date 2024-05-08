use std::cell::RefCell;
use std::collections::HashMap;

use lexical_sort::{natural_lexical_cmp, StringSort};
use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};

use crate::helpers::create::{create_comma, create_newline};
use crate::helpers::string::{load_text, update_string};

pub fn transform_array<F>(node: &SyntaxNode, transform: &F)
where
    F: Fn(&str) -> String,
{
    for array in node.children_with_tokens() {
        if array.kind() == SyntaxKind::ARRAY {
            for array_entry in array.as_node().unwrap().children_with_tokens() {
                if array_entry.kind() == SyntaxKind::VALUE {
                    update_string(array_entry.as_node().unwrap(), transform);
                }
            }
        }
    }
}

pub fn sort_array<F>(node: &SyntaxNode, transform: F)
where
    F: Fn(&str) -> String,
{
    for array in node.children_with_tokens() {
        if array.kind() == SyntaxKind::ARRAY {
            let array_node = array.as_node().unwrap();
            let mut value_set = Vec::<Vec<SyntaxElement>>::new();
            let entry_set = RefCell::new(Vec::<SyntaxElement>::new());
            let mut key_to_pos = HashMap::<String, usize>::new();

            let mut add_to_value_set = |entry: String| {
                let mut entry_set_borrow = entry_set.borrow_mut();
                if !entry_set_borrow.is_empty() {
                    key_to_pos.insert(entry.clone(), value_set.len());
                    value_set.push(entry_set_borrow.clone());
                    entry_set_borrow.clear();
                }
            };
            let mut entries = Vec::<SyntaxElement>::new();
            let mut has_value = false;
            let mut previous_is_value = false;
            let mut previous_is_bracket_open = false;
            let mut entry_value = String::from("");
            let mut count = 0;

            for entry in array_node.children_with_tokens() {
                count += 1;
                if previous_is_value {
                    // make sure ends with trailing comma
                    previous_is_value = false;
                    if entry.kind() != SyntaxKind::COMMA {
                        entry_set.borrow_mut().push(create_comma());
                    }
                }
                if previous_is_bracket_open {
                    // make sure ends with trailing comma
                    if entry.kind() == SyntaxKind::NEWLINE || entry.kind() == SyntaxKind::WHITESPACE {
                        continue;
                    }
                    previous_is_bracket_open = false;
                }
                match &entry.kind() {
                    SyntaxKind::BRACKET_START => {
                        entries.push(entry);
                        entries.push(create_newline());
                        previous_is_bracket_open = true;
                    }
                    SyntaxKind::BRACKET_END => {
                        if has_value {
                            add_to_value_set(entry_value.clone());
                        } else {
                            entries.extend(entry_set.borrow_mut().clone());
                        }
                        entries.push(entry);
                    }
                    SyntaxKind::VALUE => {
                        if has_value {
                            entry_set.borrow_mut().push(create_newline());
                            add_to_value_set(entry_value.clone());
                        }
                        has_value = true;
                        let value_node = entry.as_node().unwrap();
                        let mut found_string = false;
                        for child in value_node.children_with_tokens() {
                            let kind = child.kind();
                            if kind == SyntaxKind::STRING {
                                entry_value =
                                    transform(load_text(child.as_token().unwrap().text(), SyntaxKind::STRING).as_str());
                                found_string = true;
                                break;
                            }
                        }
                        if !found_string {
                            // abort if not correct types
                            return;
                        }
                        entry_set.borrow_mut().push(entry);
                        previous_is_value = true;
                    }
                    SyntaxKind::NEWLINE => {
                        entry_set.borrow_mut().push(entry);
                        if has_value {
                            add_to_value_set(entry_value.clone());
                            has_value = false;
                        }
                    }
                    _ => {
                        entry_set.borrow_mut().push(entry);
                    }
                }
            }

            let mut order: Vec<String> = key_to_pos.clone().into_keys().collect();
            order.string_sort_unstable(natural_lexical_cmp);
            let end = entries.split_off(2);
            for key in order {
                entries.extend(value_set[key_to_pos[&key]].clone());
            }
            entries.extend(end);
            array_node.splice_children(0..count, entries);
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

    use crate::helpers::array::{sort_array, transform_array};
    use crate::helpers::pep508::format_requirement;

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
        let root_ast = parse(start).into_syntax().clone_for_update();
        for children in root_ast.children_with_tokens() {
            if children.kind() == SyntaxKind::ENTRY {
                for entry in children.as_node().unwrap().children_with_tokens() {
                    if entry.kind() == SyntaxKind::VALUE {
                        transform_array(entry.as_node().unwrap(), &|s| format_requirement(s, keep_full_version));
                    }
                }
            }
        }
        let res = format_syntax(root_ast, Options::default());
        assert_eq!(expected, res);
    }

    #[rstest]
    #[case::empty(
        indoc ! {r#"
    a = []
    "#},
        indoc ! {r#"
    a = [
    ]
    "#}
    )]
    #[case::single(
        indoc ! {r#"
    a = ["A"]
    "#},
        indoc ! {r#"
    a = [
      "A",
    ]
    "#}
    )]
    #[case::newline_single(
        indoc ! {r#"
    a = [
      "A"
    ]
    "#},
        indoc ! {r#"
    a = [
      "A",
    ]
    "#}
    )]
    #[case::newline_single_comment(
        indoc ! {r#"
    a = [ # comment
      "A"
    ]
    "#},
        indoc ! {r#"
    a = [
      # comment
      "A",
    ]
    "#}
    )]
    #[case::increasing(
        indoc ! {r#"
    a=["B", "D",
       # C comment
       "C", # C trailing
       # A comment
       "A" # A trailing
      # extra
    ] # array comment
    "#},
        indoc ! {r#"
    a = [
      # A comment
      "A", # A trailing
      "B",
      # C comment
      "C", # C trailing
      "D",
      # extra
    ] # array comment
    "#}
    )]
    fn test_order_array(#[case] start: &str, #[case] expected: &str) {
        let root_ast = parse(start).into_syntax().clone_for_update();
        for children in root_ast.children_with_tokens() {
            if children.kind() == SyntaxKind::ENTRY {
                for entry in children.as_node().unwrap().children_with_tokens() {
                    if entry.kind() == SyntaxKind::VALUE {
                        sort_array(entry.as_node().unwrap(), |e| e.to_lowercase());
                    }
                }
            }
        }
        let opt = Options {
            column_width: 1,
            ..Options::default()
        };
        let res = format_syntax(root_ast, opt);
        assert_eq!(res, expected);
    }
}

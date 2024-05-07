use std::cell::RefCell;
use std::collections::HashMap;

use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};

use crate::helpers::create::{create_comma, create_newline, create_string_node};
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

pub fn sort_array(node: &SyntaxNode, transform: fn(String) -> String) {
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
                        let mut has_string_value = false;
                        for e in entry.as_node().unwrap().children_with_tokens() {
                            if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&e.kind()) {
                                has_string_value = true;
                                let found = e.as_token().unwrap().text().to_string();
                                let got = found[1..found.len() - 1].to_string();
                                entry_value = transform(got);
                                break;
                            }
                        }
                        if !has_string_value {
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
            order.sort();
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

    use crate::helpers::array::{array_pep508_normalize, sort_array};

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
                        array_pep508_normalize(entry.as_node().unwrap(), keep_full_version);
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

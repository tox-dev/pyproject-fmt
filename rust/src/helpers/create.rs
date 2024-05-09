use taplo::parser::parse;
use taplo::syntax::{SyntaxElement, SyntaxKind};

pub fn make_string_node(text: &str) -> SyntaxElement {
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
    panic!("Could not create string element for {text:?}")
}

pub fn make_empty_newline() -> SyntaxElement {
    for root in parse("\n\n").into_syntax().clone_for_update().children_with_tokens() {
        if root.kind() == SyntaxKind::NEWLINE {
            return root;
        }
    }
    panic!("Could not create empty newline");
}

pub fn make_newline() -> SyntaxElement {
    for root in parse("\n").into_syntax().clone_for_update().children_with_tokens() {
        if root.kind() == SyntaxKind::NEWLINE {
            return root;
        }
    }
    panic!("Could not create newline");
}

pub fn make_comma() -> SyntaxElement {
    for root in parse("a=[1,2]").into_syntax().clone_for_update().children_with_tokens() {
        if root.kind() == SyntaxKind::ENTRY {
            for value in root.as_node().unwrap().children_with_tokens() {
                if value.kind() == SyntaxKind::VALUE {
                    for array in value.as_node().unwrap().children_with_tokens() {
                        if array.kind() == SyntaxKind::ARRAY {
                            for e in array.as_node().unwrap().children_with_tokens() {
                                if e.kind() == SyntaxKind::COMMA {
                                    return e;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    panic!("Could not create comma");
}

pub fn make_key(text: &str) -> SyntaxElement {
    for root in parse(format!("{text}=1").as_str())
        .into_syntax()
        .clone_for_update()
        .children_with_tokens()
    {
        if root.kind() == SyntaxKind::ENTRY {
            for value in root.as_node().unwrap().children_with_tokens() {
                if value.kind() == SyntaxKind::KEY {
                    return value;
                }
            }
        }
    }
    panic!("Could not create key {text}");
}

pub fn make_array(key: &str) -> SyntaxElement {
    let txt = format!("{key} = []");
    for root in parse(txt.as_str())
        .into_syntax()
        .clone_for_update()
        .children_with_tokens()
    {
        if root.kind() == SyntaxKind::ENTRY {
            return root;
        }
    }
    panic!("Could not create array");
}

pub fn make_array_entry(key: &str) -> SyntaxElement {
    let txt = format!("a = [\"{key}\"]");
    for root in parse(txt.as_str())
        .into_syntax()
        .clone_for_update()
        .children_with_tokens()
    {
        if root.kind() == SyntaxKind::ENTRY {
            for value in root.as_node().unwrap().children_with_tokens() {
                if value.kind() == SyntaxKind::VALUE {
                    for array in value.as_node().unwrap().children_with_tokens() {
                        if array.kind() == SyntaxKind::ARRAY {
                            for e in array.as_node().unwrap().children_with_tokens() {
                                if e.kind() == SyntaxKind::VALUE {
                                    return e;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    panic!("Could not create array");
}

pub fn make_entry_of_string(key: &String, value: &String) -> SyntaxElement {
    let txt = format!("{key} = \"{value}\"\n");
    for root in parse(txt.as_str())
        .into_syntax()
        .clone_for_update()
        .children_with_tokens()
    {
        if root.kind() == SyntaxKind::ENTRY {
            return root;
        }
    }
    panic!("Could not create entry of string");
}

pub fn make_table_entry(key: &str) -> Vec<SyntaxElement> {
    let txt = format!("[{key}]\n");
    let mut res = Vec::<SyntaxElement>::new();
    for root in parse(txt.as_str())
        .into_syntax()
        .clone_for_update()
        .children_with_tokens()
    {
        res.push(root);
    }
    res
}

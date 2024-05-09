use taplo::parser::parse;
use taplo::syntax::{SyntaxElement, SyntaxKind};

pub fn create_string_node(text: String) -> SyntaxElement {
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
    panic!("Could not create string element for {:?}", text)
}

pub fn create_empty_newline() -> SyntaxElement {
    for root in parse("\n\n").into_syntax().clone_for_update().children_with_tokens() {
        if root.kind() == SyntaxKind::NEWLINE {
            return root;
        }
    }
    panic!("Could not create empty newline");
}

pub fn create_newline() -> SyntaxElement {
    for root in parse("\n").into_syntax().clone_for_update().children_with_tokens() {
        if root.kind() == SyntaxKind::NEWLINE {
            return root;
        }
    }
    panic!("Could not create newline");
}

pub fn create_comma() -> SyntaxElement {
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

pub fn create_key(text: String) -> SyntaxElement {
    for root in parse(format!("{}=1", text).as_str())
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
    panic!("Could not create key {}", text);
}

pub fn create_array(key: &str) -> SyntaxElement {
    let txt = format!("{} = []", key);
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

pub fn create_array_entry(key: String) -> SyntaxElement {
    let txt = format!("a = [\"{}\"]", key);
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

pub fn create_table_entry(key: &str) -> Vec<SyntaxElement> {
    let txt = format!("[{}]\n", key);
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

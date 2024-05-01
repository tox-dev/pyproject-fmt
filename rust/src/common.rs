use taplo::parser::parse;
use taplo::syntax::{SyntaxElement, SyntaxKind};

pub fn get_table_name(entry: &SyntaxElement) -> String {
    if [SyntaxKind::TABLE_HEADER, SyntaxKind::TABLE_ARRAY_HEADER].contains(&entry.kind()) {
        for child in entry.as_node().unwrap().children_with_tokens() {
            if child.kind() == SyntaxKind::KEY {
                return child.as_node().unwrap().text().to_string().trim().to_string();
            }
        }
    }
    String::new()
}

pub fn create_string_node(element: SyntaxElement, text: String) -> SyntaxElement {
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

pub fn create_empty_newline() -> SyntaxElement {
    for root in parse("\n\n").into_syntax().clone_for_update().children_with_tokens() {
        if root.kind() == SyntaxKind::NEWLINE {
            return root;
        }
    }
    panic!("Could not create newline");
}

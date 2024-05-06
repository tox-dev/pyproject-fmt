use taplo::parser::parse;
use taplo::syntax::{SyntaxElement, SyntaxKind};

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

use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};

use crate::helpers::create::make_string_node;

pub fn load_text(value: &str, kind: SyntaxKind) -> String {
    let mut chars = value.chars();
    let offset = if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&kind) {
        1
    } else if kind == SyntaxKind::IDENT {
        0
    } else {
        3
    };
    for _ in 0..offset {
        chars.next();
    }
    for _ in 0..offset {
        chars.next_back();
    }
    let mut res = chars.as_str().to_string();
    if kind == SyntaxKind::STRING {
        res = res.replace("\\\"", "\"");
    }
    res
}

pub fn update_content<F>(entry: &SyntaxNode, transform: F)
where
    F: Fn(&str) -> String,
{
    let (mut to_insert, mut count) = (Vec::<SyntaxElement>::new(), 0);
    let mut changed = false;
    for mut child in entry.children_with_tokens() {
        count += 1;
        let kind = child.kind();
        if [
            SyntaxKind::STRING,
            SyntaxKind::STRING_LITERAL,
            SyntaxKind::MULTI_LINE_STRING,
            SyntaxKind::MULTI_LINE_STRING_LITERAL,
        ]
        .contains(&kind)
        {
            let found_str_value = load_text(child.as_token().unwrap().text(), kind);
            let output = transform(found_str_value.as_str());

            changed = output != found_str_value || kind != SyntaxKind::STRING;
            if changed {
                child = make_string_node(output.as_str());
            }
        }
        to_insert.push(child);
    }
    if changed {
        entry.splice_children(0..count, to_insert);
    }
}

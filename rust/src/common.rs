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

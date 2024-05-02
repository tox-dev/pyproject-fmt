use std::cell::RefCell;
use std::collections::HashMap;

use taplo::parser::parse;
use taplo::syntax::SyntaxKind::{TABLE_ARRAY_HEADER, TABLE_HEADER};
use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};
use taplo::HashSet;

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

pub fn reorder_table_keys(table: &mut Vec<SyntaxElement>, order: &[&str]) {
    let (key_to_pos, key_set) = load_keys(table);
    let mut to_insert = Vec::<SyntaxElement>::new();
    let mut handled = HashSet::<usize>::new();
    for key in order {
        if key_to_pos.contains_key(*key) {
            let pos = key_to_pos[*key];
            to_insert.extend(key_set[pos].clone());
            handled.insert(pos);
        }
    }
    for (at, entry) in key_set.into_iter().enumerate() {
        if !handled.contains(&at) {
            to_insert.extend(entry);
        }
    }
    table.splice(0..table.len(), to_insert);
}

fn load_keys(table: &Vec<SyntaxElement>) -> (HashMap<String, usize>, Vec<Vec<SyntaxElement>>) {
    let mut key_to_pos = HashMap::<String, usize>::new();
    let mut key_set = Vec::<Vec<SyntaxElement>>::new();
    let entry_set = RefCell::new(Vec::<SyntaxElement>::new());
    let mut add_to_key_set = |k| {
        let mut entry_set_borrow = entry_set.borrow_mut();
        if !entry_set_borrow.is_empty() {
            key_to_pos.insert(k, key_set.len());
            key_set.push(entry_set_borrow.clone());
            entry_set_borrow.clear();
        }
    };
    let mut key = String::from("");
    for c in table {
        if c.kind() == SyntaxKind::ENTRY {
            add_to_key_set(key.clone());
            for e in c.as_node().unwrap().children_with_tokens() {
                if e.kind() == SyntaxKind::KEY {
                    key = e.as_node().unwrap().text().to_string().trim().to_string();
                    break;
                }
            }
        }
        entry_set.borrow_mut().push(c.clone());
    }
    add_to_key_set(key.clone());
    (key_to_pos, key_set)
}

pub fn for_entries<F>(table: &mut Vec<SyntaxElement>, f: &mut F)
where
    F: FnMut(String, &SyntaxNode),
{
    let mut key = String::new();
    for table_entry in table {
        if table_entry.kind() == SyntaxKind::ENTRY {
            for entry in table_entry.as_node().unwrap().children_with_tokens() {
                if entry.kind() == SyntaxKind::KEY {
                    key = entry.as_node().unwrap().text().to_string().trim().to_string();
                } else if entry.kind() == SyntaxKind::VALUE {
                    f(key.clone(), entry.as_node().unwrap());
                }
            }
        }
    }
}

#[derive(Debug)]
pub struct Tables {
    pub header_to_pos: HashMap<String, usize>,
    pub table_set: Vec<Vec<SyntaxElement>>,
}

impl Tables {
    pub(crate) fn get(&mut self, key: &String) -> Option<&mut Vec<SyntaxElement>> {
        if self.header_to_pos.contains_key(key) {
            Some(&mut self.table_set[self.header_to_pos[key]])
        } else {
            None
        }
    }

    pub fn from_ast(root_ast: &mut SyntaxNode) -> Tables {
        let mut header_to_pos = HashMap::<String, usize>::new();
        let mut table_set = Vec::<Vec<SyntaxElement>>::new();
        let entry_set = RefCell::new(Vec::<SyntaxElement>::new());
        let mut add_to_table_set = || {
            let mut entry_set_borrow = entry_set.borrow_mut();
            if !entry_set_borrow.is_empty() {
                header_to_pos.insert(get_table_name(&entry_set_borrow[0]), table_set.len());
                table_set.push(entry_set_borrow.clone());
                entry_set_borrow.clear();
            }
        };
        for c in root_ast.children_with_tokens() {
            if [TABLE_ARRAY_HEADER, TABLE_HEADER].contains(&c.kind()) {
                add_to_table_set();
            }
            entry_set.borrow_mut().push(c);
        }
        add_to_table_set();

        Tables {
            header_to_pos,
            table_set,
        }
    }
}

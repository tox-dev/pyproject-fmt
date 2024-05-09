use std::cell::{RefCell, RefMut};
use std::collections::HashMap;
use std::iter::zip;

use taplo::syntax::SyntaxKind::{TABLE_ARRAY_HEADER, TABLE_HEADER};
use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};
use taplo::HashSet;

use crate::helpers::create::{make_empty_newline, make_key, make_newline, make_table_entry};
use crate::helpers::string::load_text;

#[derive(Debug)]
pub struct Tables {
    pub header_to_pos: HashMap<String, usize>,
    pub table_set: Vec<RefCell<Vec<SyntaxElement>>>,
}

impl Tables {
    pub(crate) fn get(&mut self, key: &str) -> Option<&RefCell<Vec<SyntaxElement>>> {
        if self.header_to_pos.contains_key(key) {
            Some(&self.table_set[self.header_to_pos[key]])
        } else {
            None
        }
    }

    pub fn from_ast(root_ast: &SyntaxNode) -> Self {
        let mut header_to_pos = HashMap::<String, usize>::new();
        let mut table_set = Vec::<RefCell<Vec<SyntaxElement>>>::new();
        let entry_set = RefCell::new(Vec::<SyntaxElement>::new());
        let mut add_to_table_set = || {
            let mut entry_set_borrow = entry_set.borrow_mut();
            if !entry_set_borrow.is_empty() {
                header_to_pos.insert(get_table_name(&entry_set_borrow[0]), table_set.len());
                table_set.push(RefCell::new(entry_set_borrow.clone()));
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

        Self {
            header_to_pos,
            table_set,
        }
    }

    pub fn reorder(&mut self, root_ast: &SyntaxNode, order: &[&str]) {
        let mut to_insert = Vec::<SyntaxElement>::new();
        let mut entry_count: usize = 0;

        let order = calculate_order(&self.header_to_pos, order);
        let mut next = order.clone();
        if !next.is_empty() {
            next.remove(0);
        }
        next.push(String::new());
        for (name, next_name) in zip(order.iter(), next.iter()) {
            let mut entries = self.get(name).unwrap().borrow().clone();
            if entries.is_empty() {
                continue;
            }
            entry_count += entries.len();
            let last = entries.last().unwrap();
            if name.is_empty() && last.kind() == SyntaxKind::NEWLINE && entries.len() == 1 {
                continue;
            }
            if last.kind() == SyntaxKind::NEWLINE && get_key(name) != get_key(next_name) {
                entries.splice(entries.len() - 1..entries.len(), [make_empty_newline()]);
            }
            to_insert.extend(entries);
        }
        root_ast.splice_children(0..entry_count, to_insert);
    }
}

fn calculate_order(header_to_pos: &HashMap<String, usize>, ordering: &[&str]) -> Vec<String> {
    let max_ordering = ordering.len() * 2;
    let key_to_pos = ordering
        .iter()
        .enumerate()
        .map(|(k, v)| (v, k * 2))
        .collect::<HashMap<&&str, usize>>();

    let mut order: Vec<String> = header_to_pos.clone().into_keys().collect();
    order.sort_by_cached_key(|k| -> usize {
        let key = get_key(k);
        let pos = key_to_pos.get(&key.as_str());
        if pos.is_some() {
            let offset = usize::from(key != *k);
            pos.unwrap() + offset
        } else {
            max_ordering + header_to_pos[k]
        }
    });
    order
}

fn get_key(k: &str) -> String {
    let parts: Vec<&str> = k.splitn(3, '.').collect();
    if !parts.is_empty() {
        return if parts[0] == "tool" && parts.len() >= 2 {
            parts[0..2].join(".")
        } else {
            String::from(parts[0])
        };
    }
    String::from(k)
}

pub fn reorder_table_keys(table: &mut RefMut<Vec<SyntaxElement>>, order: &[&str]) {
    let size = table.len();
    let (key_to_pos, key_set) = load_keys(table);
    let mut to_insert = Vec::<SyntaxElement>::new();
    let mut handled = HashSet::<usize>::new();
    for key in order {
        let mut parts = key_to_pos
            .keys()
            .filter(|k| {
                key == k || (k.starts_with(key) && k.len() > key.len() && k.chars().nth(key.len()).unwrap() == '.')
            })
            .clone()
            .collect::<Vec<&String>>();
        parts.sort_by_key(|s| s.to_lowercase().replace('"', ""));
        for element in parts {
            let pos = key_to_pos[element];
            to_insert.extend(key_set[pos].clone());
            handled.insert(pos);
        }
    }
    for (at, entry) in key_set.into_iter().enumerate() {
        if !handled.contains(&at) {
            to_insert.extend(entry);
        }
    }
    table.splice(0..size, to_insert);
}

fn load_keys(table: &RefMut<Vec<SyntaxElement>>) -> (HashMap<String, usize>, Vec<Vec<SyntaxElement>>) {
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
    let mut key = String::new();
    for c in table.iter() {
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
    add_to_key_set(key);
    (key_to_pos, key_set)
}

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

pub fn for_entries<F>(table: &RefMut<Vec<SyntaxElement>>, f: &mut F)
where
    F: FnMut(String, &SyntaxNode),
{
    let mut key = String::new();
    for table_entry in table.iter() {
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

pub fn collapse_sub_tables(tables: &mut Tables, name: &str) {
    let h2p = tables.header_to_pos.clone();
    let sub_name_prefix = format!("{name}.");
    let sub_table_keys: Vec<&String> = h2p.keys().filter(|s| s.starts_with(sub_name_prefix.as_str())).collect();
    if sub_table_keys.is_empty() {
        return;
    }
    if !tables.header_to_pos.contains_key(name) {
        tables.header_to_pos.insert(String::from(name), tables.table_set.len());
        tables.table_set.push(RefCell::new(make_table_entry(name)));
    }
    let mut main = tables.table_set[tables.header_to_pos[name]].borrow_mut();
    for key in sub_table_keys {
        let mut sub = tables.table_set[tables.header_to_pos[key]].borrow_mut();
        let sub_name = key.strip_prefix(sub_name_prefix.as_str()).unwrap();
        let mut header = false;
        for child in sub.iter() {
            let kind = child.kind();
            if kind == SyntaxKind::TABLE_HEADER {
                header = true;
                continue;
            }
            if header && kind == SyntaxKind::NEWLINE {
                continue;
            }
            if kind == SyntaxKind::ENTRY {
                let mut to_insert = Vec::<SyntaxElement>::new();
                let child_node = child.as_node().unwrap();
                for mut entry in child_node.children_with_tokens() {
                    if entry.kind() == SyntaxKind::KEY {
                        for array_entry_value in entry.as_node().unwrap().children_with_tokens() {
                            if array_entry_value.kind() == SyntaxKind::IDENT {
                                let txt = load_text(array_entry_value.as_token().unwrap().text(), SyntaxKind::IDENT);
                                entry = make_key(format!("{sub_name}.{txt}").as_str());
                                break;
                            }
                        }
                    }
                    to_insert.push(entry);
                }
                child_node.splice_children(0..to_insert.len(), to_insert);
            }
            if main.last().unwrap().kind() != SyntaxKind::NEWLINE {
                main.push(make_newline());
            }
            main.push(child.clone());
        }
        sub.clear();
    }
}

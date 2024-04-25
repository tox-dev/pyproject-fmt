use std::cell::RefCell;
use std::cmp::Ordering;
use std::collections::HashMap;
use std::ops::Index;

use taplo::rowan::{NodeOrToken, SyntaxElement};
use taplo::syntax::SyntaxKind::{TABLE_ARRAY_HEADER, TABLE_HEADER};
use taplo::syntax::{Lang, SyntaxNode};

type Element = SyntaxElement<Lang>;

pub fn reorder_table(root_ast: &mut SyntaxNode) {
    let (header_to_pos, table_set) = load_tables(root_ast);
    let mut to_insert = Vec::<Element>::new();
    let mut entry_count: usize = 0;
    for key in calculate_order(&header_to_pos) {
        let entries = table_set[key].clone();
        entry_count += entries.len();
        to_insert.extend(entries);
    }
    root_ast.splice_children(0..entry_count, to_insert);
}

fn calculate_order(header_to_pos: &HashMap<String, usize>) -> Vec<usize> {
    let tool_order = [
        // Build backends
        "poetry",
        "poetry-dynamic-versioning",
        "pdm",
        "setuptools",
        "distutils",
        "setuptools_scm",
        "hatch",
        "flit",
        "scikit-build",
        "meson-python",
        "maturin",
        "whey",
        "py-build-cmake",
        "sphinx-theme-builder",
        // Builders
        "cibuildwheel",
        // Formatters and linters
        "autopep8",
        "black",
        "ruff",
        "isort",
        "flake8",
        "pycln",
        "nbqa",
        "pylint",
        "repo-review",
        "codespell",
        "docformatter",
        "pydoclint",
        "tomlsort",
        "check-manifest",
        "check-sdist",
        "check-wheel-contents",
        "deptry",
        "pyproject-fmt",
        // Testing
        "pytest",
        "pytest_env",
        "pytest-enabler",
        "coverage",
        // Runners
        "doit",
        "spin",
        "tox",
        // Releasers/bumpers
        "bumpversion",
        "jupyter-releaser",
        "tbump",
        "towncrier",
        "vendoring",
        // Type checking
        "mypy",
        "pyright",
    ];
    let max = tool_order.len();
    let tool_order_to_pos = tool_order
        .iter()
        .enumerate()
        .map(|(k, v)| (v, k))
        .collect::<HashMap<&&str, usize>>();
    let mut order: Vec<String> = header_to_pos.clone().into_keys().collect();
    order.sort_by(|l, r| {
        if l.starts_with("tool.") && r.starts_with("tool.") {
            let ls: Vec<&str> = l.splitn(3, '.').collect();
            let rs: Vec<&str> = r.splitn(3, '.').collect();
            let lp = tool_order_to_pos.get(ls.index(1)).unwrap_or(&max);
            let rp = tool_order_to_pos.get(rs.index(1)).unwrap_or(&max);
            let c = lp.cmp(rp);
            if c == Ordering::Equal {
                ls.get(2).unwrap_or(&"").cmp(rs.get(2).unwrap_or(&""))
            } else {
                c
            }
        } else if l.starts_with("tool.") {
            Ordering::Greater
        } else if r.starts_with("tool.") {
            Ordering::Less
        } else {
            l.cmp(r)
        }
    });
    order.iter().map(|k| *header_to_pos.index(k)).collect::<Vec<usize>>()
}

fn load_tables(root_ast: &mut SyntaxNode) -> (HashMap<String, usize>, Vec<Vec<Element>>) {
    let mut header_to_pos = HashMap::<String, usize>::new();
    let mut table_set = Vec::<Vec<Element>>::new();
    let entry_set = RefCell::new(Vec::<Element>::new());
    let mut add_to_table_set = || {
        let mut entry_set_borrow = entry_set.borrow_mut();
        if !entry_set_borrow.is_empty() {
            header_to_pos.insert(get_header(entry_set_borrow[0].clone()), table_set.len());
            table_set.push(entry_set_borrow.clone());
            entry_set_borrow.clear();
        }
    };
    for c in root_ast.children_with_tokens() {
        match c.clone() {
            NodeOrToken::Node(node) => {
                match node.kind() {
                    TABLE_ARRAY_HEADER | TABLE_HEADER => {
                        add_to_table_set();
                    }
                    _ => {}
                };
            }
            NodeOrToken::Token(_) => {}
        }
        entry_set.borrow_mut().push(c);
    }
    add_to_table_set();

    (header_to_pos, table_set)
}

fn get_header(entry: Element) -> String {
    let mut header = String::new();
    match entry {
        NodeOrToken::Node(node) => {
            for child in node.children_with_tokens() {
                match child {
                    NodeOrToken::Node(child_node) => {
                        header = format!("{}", child_node.text());
                    }
                    NodeOrToken::Token(_) => {}
                }
            }
        }
        NodeOrToken::Token(_) => {}
    }
    header
}

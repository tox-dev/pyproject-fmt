use std::cell::RefCell;
use std::collections::HashMap;
use std::iter::zip;
use std::ops::Index;

use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};
use taplo::syntax::SyntaxKind::{TABLE_ARRAY_HEADER, TABLE_HEADER};

use crate::common::{create_empty_newline, get_table_name};

pub fn reorder_table(root_ast: &mut SyntaxNode) {
    let (header_to_pos, table_set) = load_tables(root_ast);
    let mut to_insert = Vec::<SyntaxElement>::new();
    let mut entry_count: usize = 0;

    let order = calculate_order(&header_to_pos);
    let mut next = order.clone();
    next.remove(0);
    next.push(String::from(""));
    for (name, next_name) in zip(order.iter(), next.iter()) {
        let index = header_to_pos.index(name);
        let mut entries = table_set[*index].clone();
        entry_count += entries.len();
        let last = entries.last().unwrap();
        if name.is_empty() && last.kind() == SyntaxKind::NEWLINE && entries.len() == 1 {
            continue;
        }
        if last.kind() == SyntaxKind::NEWLINE && get_key(name) != get_key(next_name) {
            entries.splice(entries.len() - 1..entries.len(), [create_empty_newline()]);
        }
        to_insert.extend(entries);
    }
    root_ast.splice_children(0..entry_count, to_insert);
}

fn calculate_order(header_to_pos: &HashMap<String, usize>) -> Vec<String> {
    let ordering = [
        "",
        "build-system",
        "project",
        // Build backends
        "tool.poetry",
        "tool.poetry-dynamic-versioning",
        "tool.pdm",
        "tool.setuptools",
        "tool.distutils",
        "tool.setuptools_scm",
        "tool.hatch",
        "tool.flit",
        "tool.scikit-build",
        "tool.meson-python",
        "tool.maturin",
        "tool.whey",
        "tool.py-build-cmake",
        "tool.sphinx-theme-builder",
        // Builders
        "tool.cibuildwheel",
        // Formatters and linters
        "tool.autopep8",
        "tool.black",
        "tool.ruff",
        "tool.isort",
        "tool.flake8",
        "tool.pycln",
        "tool.nbqa",
        "tool.pylint",
        "tool.repo-review",
        "tool.codespell",
        "tool.docformatter",
        "tool.pydoclint",
        "tool.tomlsort",
        "tool.check-manifest",
        "tool.check-sdist",
        "tool.check-wheel-contents",
        "tool.deptry",
        "tool.pyproject-fmt",
        // Testing
        "tool.pytest",
        "tool.pytest_env",
        "tool.pytest-enabler",
        "tool.coverage",
        // Runners
        "tool.doit",
        "tool.spin",
        "tool.tox",
        // Releasers/bumpers
        "tool.bumpversion",
        "tool.jupyter-releaser",
        "tool.tbump",
        "tool.towncrier",
        "tool.vendoring",
        // Type checking
        "tool.mypy",
        "tool.pyright",
    ];
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
            let offset = if key == *k { 0 } else { 1 };
            pos.unwrap() + offset
        } else {
            max_ordering + header_to_pos[k]
        }
    });
    order
}

fn load_tables(root_ast: &mut SyntaxNode) -> (HashMap<String, usize>, Vec<Vec<SyntaxElement>>) {
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

    (header_to_pos, table_set)
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

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;

    use crate::table_ordering::reorder_table;

    #[rstest]
    #[case::reorder(
    indoc ! {r#"
    # comment
    a= "b"
    [project]
    name="alpha"
    dependencies=["e"]
    [build-system]
    build-backend="backend"
    requires=["c", "d"]
    [tool.mypy]
    mk="mv"
    [tool.ruff.test]
    mrt="vrt"
    [extra]
    ek = "ev"
    [tool.undefined]
    mu="mu"
    [tool.ruff]
    mr="vr"
    [demo]
    ed = "ed"
    [tool.pytest]
    mk="mv"
    "#},
    indoc ! {r#"
    # comment
    a = "b"

    [build-system]
    build-backend = "backend"
    requires = ["c", "d"]

    [project]
    name = "alpha"
    dependencies = ["e"]

    [tool.ruff]
    mr = "vr"
    [tool.ruff.test]
    mrt = "vrt"

    [tool.pytest]
    mk = "mv"

    [tool.mypy]
    mk = "mv"

    [extra]
    ek = "ev"

    [tool.undefined]
    mu = "mu"

    [demo]
    ed = "ed"
    "#},
    )]
    fn test_reorder_table(#[case] start: &str, #[case] expected: &str) {
        let mut root_ast = parse(start).into_syntax().clone_for_update();
        reorder_table(&mut root_ast);
        let got = format_syntax(root_ast, Options::default());
        assert_eq!(got, expected);
    }
}

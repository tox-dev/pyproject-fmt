use regex::Regex;
use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};
use taplo::HashSet;

use crate::helpers::array::{array_pep508_normalize, sort_array};
use crate::helpers::create::{create_array, create_array_entry, create_comma, create_string_node};
use crate::helpers::pep508::req_name;
use crate::helpers::table::{for_entries, reorder_table_keys};

pub fn fix_project(table: &mut Vec<SyntaxElement>, keep_full_version: bool, max_supported_python: (u8, u8)) {
    generate_classifiers(table, max_supported_python);
    for_entries(table, &mut |key, entry| match key.as_str() {
        "name" => {
            let mut to_insert = Vec::<SyntaxElement>::new();
            for mut element in entry.children_with_tokens() {
                if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&element.kind()) {
                    let found = element.as_token().unwrap().text().to_string();
                    element = create_string_node(req_name(&found[1..found.len() - 1]));
                    to_insert.push(element);
                }
            }
            entry.splice_children(0..to_insert.len(), to_insert);
        }
        "dependencies" => {
            array_pep508_normalize(entry, keep_full_version);
            sort_array(entry, |e| req_name(e.as_str()).to_lowercase());
        }
        "dynamic" | "keywords" => {
            sort_array(entry, |e| e.to_lowercase());
        }
        "classifiers" => {
            sort_array(entry, |e| e.as_str().to_lowercase());
        }
        _ => {}
    });
    reorder_table_keys(
        table,
        &[
            "",
            "name",
            "version",
            "description",
            "readme",
            "keywords",
            "license",
            "license-files",
            "maintainers",
            "authors",
            "requires-python",
            "classifiers",
            "dynamic",
            "dependencies",
            // these go at the end as they may be inline or exploded
            "optional-dependencies",
            "urls",
            "scripts",
            "gui-scripts",
            "entry-points",
        ],
    );
}

fn generate_classifiers(table: &mut Vec<SyntaxElement>, max_supported_python: (u8, u8)) {
    let (min, max, omit, classifiers) = get_python_requires_with_classifier(table, max_supported_python);
    match classifiers {
        None => {
            let entry = create_array("classifiers");
            generate_classifiers_to_entry(entry.as_node().unwrap(), min, max, omit, HashSet::new());
            table.push(entry);
        }
        Some(c) => {
            let mut key_value = String::new();
            for table_row in table {
                if table_row.kind() == SyntaxKind::ENTRY {
                    for entry in table_row.as_node().unwrap().children_with_tokens() {
                        if entry.kind() == SyntaxKind::KEY {
                            key_value = entry.as_node().unwrap().text().to_string().trim().to_string();
                        } else if entry.kind() == SyntaxKind::VALUE && key_value == "classifiers" {
                            generate_classifiers_to_entry(
                                table_row.as_node().unwrap(),
                                min,
                                max,
                                omit.clone(),
                                c.clone(),
                            );
                        }
                    }
                }
            }
        }
    };
}

fn generate_classifiers_to_entry(
    node: &SyntaxNode,
    min: (u8, u8),
    max: (u8, u8),
    omit: Vec<u8>,
    existing: HashSet<String>,
) {
    for array in node.children_with_tokens() {
        if array.kind() == SyntaxKind::VALUE {
            for root_value in array.as_node().unwrap().children_with_tokens() {
                if root_value.kind() == SyntaxKind::ARRAY {
                    let mut must_have: HashSet<String> = HashSet::new();
                    must_have.insert(String::from("Programming Language :: Python :: 3 :: Only"));
                    must_have.extend(
                        (min.1..max.1 + 1)
                            .filter(|i| !omit.contains(i))
                            .map(|i| format!("Programming Language :: Python :: 3.{}", i)),
                    );

                    let mut count = 0;
                    let delete = existing
                        .iter()
                        .filter(|e| e.starts_with("Programming Language :: Python :: ") && !must_have.contains(*e))
                        .collect::<HashSet<&String>>();
                    let mut to_insert = Vec::<SyntaxElement>::new();

                    let mut delete_mode = false;
                    for array_entry in root_value.as_node().unwrap().children_with_tokens() {
                        count += 1;
                        let kind = array_entry.kind();
                        if delete_mode & [SyntaxKind::NEWLINE, SyntaxKind::BRACKET_END].contains(&kind) {
                            delete_mode = false;
                            if kind == SyntaxKind::NEWLINE {
                                continue;
                            }
                        } else if kind == SyntaxKind::VALUE {
                            for array_entry_value in array_entry.as_node().unwrap().children_with_tokens() {
                                if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&array_entry_value.kind())
                                {
                                    let found = array_entry_value.as_token().unwrap().text().to_string();
                                    let txt = &found[1..found.len() - 1];
                                    delete_mode = delete.contains(&String::from(txt));
                                    if delete_mode {
                                        // delete from previous comma/start until next newline
                                        let mut remove_count = to_insert.len();
                                        for (at, v) in to_insert.iter().rev().enumerate() {
                                            if [SyntaxKind::COMMA, SyntaxKind::BRACKET_START].contains(&v.kind()) {
                                                remove_count = at;
                                                for (i, e) in to_insert.iter().enumerate().skip(to_insert.len() - at) {
                                                    if e.kind() == SyntaxKind::NEWLINE {
                                                        remove_count = i + 1;
                                                        break;
                                                    }
                                                }
                                                break;
                                            }
                                        }
                                        to_insert.truncate(remove_count);
                                    }
                                    break;
                                }
                            }
                        }
                        if !delete_mode {
                            to_insert.push(array_entry);
                        }
                    }
                    let to_add: HashSet<_> = must_have.difference(&existing).collect();
                    if !to_add.is_empty() {
                        // make sure we have a comma
                        let mut trail_at = 0;
                        for (at, v) in to_insert.iter().rev().enumerate() {
                            trail_at = to_insert.len() - at;
                            if v.kind() == SyntaxKind::COMMA {
                                for (i, e) in to_insert.iter().enumerate().skip(trail_at) {
                                    if e.kind() == SyntaxKind::NEWLINE || e.kind() == SyntaxKind::BRACKET_END {
                                        trail_at = i;
                                        break;
                                    }
                                }
                                break;
                            } else if v.kind() == SyntaxKind::BRACKET_START {
                                break;
                            } else if v.kind() == SyntaxKind::VALUE {
                                to_insert.insert(trail_at, create_comma());
                                trail_at += 1;
                                break;
                            }
                        }
                        let trail = to_insert.split_off(trail_at);
                        for add in to_add {
                            to_insert.push(create_array_entry(add.clone()));
                            to_insert.push(create_comma());
                        }
                        to_insert.extend(trail);
                    }
                    root_value.as_node().unwrap().splice_children(0..count, to_insert);
                }
            }
        }
    }
}

type MaxMinPythonWithClassifier = ((u8, u8), (u8, u8), Vec<u8>, Option<HashSet<String>>);

fn get_python_requires_with_classifier(
    table: &mut Vec<SyntaxElement>,
    max_supported_python: (u8, u8),
) -> MaxMinPythonWithClassifier {
    let mut classifiers: Option<HashSet<String>> = None;
    let mut mins: Vec<u8> = vec![];
    let mut maxs: Vec<u8> = vec![];
    let mut omit: Vec<u8> = vec![];
    assert_eq!(max_supported_python.0, 3, "for now only Python 3 supported");

    for_entries(table, &mut |key, entry| {
        if key == "requires-python" {
            for child in entry.children_with_tokens() {
                if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&child.kind()) {
                    let found_text = child.as_token().unwrap().text();
                    let found_str_value: String = found_text[1..found_text.len() - 1].split_whitespace().collect();
                    let re = Regex::new(r"^(?<op><|<=|==|!=|>=|>)3[.](?<minor>\d+)").unwrap();
                    for part in found_str_value.split(',') {
                        let capture = re.captures(part);
                        if capture.is_some() {
                            let caps = capture.unwrap();
                            let minor = caps["minor"].parse::<u8>().unwrap();
                            match &caps["op"] {
                                "==" => {
                                    mins.push(minor);
                                    maxs.push(minor);
                                }
                                ">=" => {
                                    mins.push(minor);
                                }
                                ">" => {
                                    mins.push(minor + 1);
                                }
                                "<=" => {
                                    maxs.push(minor);
                                }
                                "<" => {
                                    maxs.push(minor - 1);
                                }
                                "!=" => {
                                    omit.push(minor);
                                }
                                _ => {}
                            }
                        }
                    }
                }
            }
        } else if key == "classifiers" {
            for child in entry.children_with_tokens() {
                if child.kind() == SyntaxKind::ARRAY {
                    let mut found_elements = HashSet::<String>::new();
                    for array in child.as_node().unwrap().children_with_tokens() {
                        if array.kind() == SyntaxKind::VALUE {
                            for value in array.as_node().unwrap().children_with_tokens() {
                                if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&value.kind()) {
                                    let found = value.as_token().unwrap().text();
                                    let found_str_value: String = String::from(&found[1..found.len() - 1]);
                                    found_elements.insert(found_str_value);
                                }
                            }
                        }
                    }
                    classifiers = Some(found_elements);
                }
            }
        }
    });
    let min_py = (3, *mins.iter().max().unwrap_or(&8));
    let max_py = (3, *maxs.iter().min().unwrap_or(&max_supported_python.1));
    (min_py, max_py, omit, classifiers)
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;
    use taplo::syntax::SyntaxElement;

    use crate::helpers::table::Tables;
    use crate::project::fix_project;

    fn evaluate(start: &str, keep_full_version: bool, max_supported_python: (u8, u8)) -> String {
        let mut root_ast = parse(start).into_syntax().clone_for_update();
        let mut tables = Tables::from_ast(&mut root_ast);
        match tables.get(&String::from("project")) {
            None => {}
            Some(t) => {
                fix_project(t, keep_full_version, max_supported_python);
            }
        }
        let entries = tables.table_set.into_iter().flatten().collect::<Vec<SyntaxElement>>();
        root_ast.splice_children(0..entries.len(), entries);
        let opt = Options {
            column_width: 1,
            ..Options::default()
        };
        format_syntax(root_ast, opt)
    }

    #[rstest]
    #[case::no_project(
        indoc ! {r#""#},
        "\n",
        false,
        (3, 8),
    )]
    #[case::project_requires_no_keep(
        indoc ! {r#"
    [project]
    dependencies=["a>=1.0.0", "b.c>=1.5.0"]
    "#},
        indoc ! {r#"
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "a>=1",
      "b-c>=1.5",
    ]
    "#},
        false,
        (3, 8),
    )]
    #[case::project_requires_keep(
        indoc ! {r#"
    [project]
    dependencies=["a>=1.0.0", "b.c>=1.5.0"]
    "#},
        indoc ! {r#"
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dependencies = [
      "a>=1.0.0",
      "b-c>=1.5.0",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_requires_ge(
        indoc ! {r#"
    [project]
    requires-python = " >= 3.8"
    classifiers = [
      # comment license inline 1
      # comment license inline 2
      "License :: OSI Approved :: MIT License", # comment license post
      # comment 3.12 inline 1
      # comment 3.12 inline 2
      "Programming Language :: Python :: 3.12", # comment 3.12 post
      # comment 3.10 inline
      "Programming Language :: Python :: 3.10" # comment 3.10 post
      # extra 1
      # extra 2
      # extra 3
    ]
    "#},
        indoc ! {r#"
    [project]
    requires-python = " >= 3.8"
    classifiers = [
      # comment license inline 1
      # comment license inline 2
      "License :: OSI Approved :: MIT License",      # comment license post
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      # comment 3.10 inline
      "Programming Language :: Python :: 3.10", # comment 3.10 post
      # extra 1
      # extra 2
      # extra 3
    ]
    "#},
        true,
        (3, 10),
    )]
    #[case::project_requires_gt(
        indoc ! {r#"
    [project]
    requires-python = " > 3.7"
    "#},
        indoc ! {r#"
    [project]
    requires-python = " > 3.7"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_requires_eq(
        indoc ! {r#"
    [project]
    requires-python = " == 3.12"
    "#},
        indoc ! {r#"
    [project]
    requires-python = " == 3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_sort_keywords(
        indoc ! {r#"
    [project]
    keywords = ["b", "A", "a-c", " c"]
    "#},
        indoc ! {r#"
    [project]
    keywords = [
      " c",
      "A",
      "a-c",
      "b",
    ]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_sort_dynamic(
        indoc ! {r#"
    [project]
    dynamic = ["b", "A", "a-c", " c", "a10", "a2"]
    "#},
        indoc ! {r#"
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    dynamic = [
      " c",
      "A",
      "a-c",
      "a2",
      "a10",
      "b",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_name_norm(
        indoc ! {r#"
    [project]
    name = "a.b.c"
    "#},
        indoc ! {r#"
    [project]
    name = "a-b-c"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_name_literal(
        indoc ! {r#"
    [project]
    name = 'a.b.c'
    "#},
        indoc ! {r#"
    [project]
    name = "a-b-c"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_requires_gt_old(
        indoc ! {r#"
    [project]
    requires-python = " > 3.6"
    "#},
        indoc ! {r#"
    [project]
    requires-python = " > 3.6"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_requires_range(
        indoc ! {r#"
    [project]
    requires-python=">=3.7,<3.13"
    "#},
        indoc ! {r#"
    [project]
    requires-python = ">=3.7,<3.13"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_requires_high_range(
        indoc ! {r#"
    [project]
    requires-python = "<=3.13,>3.10"
    "#},
        indoc ! {r#"
    [project]
    requires-python = "<=3.13,>3.10"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
      "Programming Language :: Python :: 3.13",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_requires_range_neq(
        indoc ! {r#"
    [project]
    requires-python = "<=3.10,!=3.9,>=3.8"
    "#},
        indoc ! {r#"
    [project]
    requires-python = "<=3.10,!=3.9,>=3.8"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.10",
    ]
    "#},
        true,
        (3, 12),
    )]
    fn test_normalize_requirement(
        #[case] start: &str,
        #[case] expected: &str,
        #[case] keep_full_version: bool,
        #[case] max_supported_python: (u8, u8),
    ) {
        assert_eq!(evaluate(start, keep_full_version, max_supported_python), expected);
    }
}

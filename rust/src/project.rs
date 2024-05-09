use std::cell::RefMut;

use regex::Regex;
use taplo::syntax::{SyntaxElement, SyntaxKind, SyntaxNode};
use taplo::util::StrExt;
use taplo::HashSet;

use crate::helpers::array::{sort_array, transform_array};
use crate::helpers::create::{create_array, create_array_entry, create_comma, create_entry_of_string, create_newline};
use crate::helpers::pep508::{format_requirement, get_canonic_requirement_name};
use crate::helpers::string::{load_text, update_string};
use crate::helpers::table::{collapse_sub_tables, for_entries, reorder_table_keys, Tables};

pub fn fix_project(
    tables: &mut Tables,
    keep_full_version: bool,
    max_supported_python: (u8, u8),
    min_supported_python: (u8, u8),
) {
    collapse_sub_tables(tables, "project");
    let table_element = tables.get(&String::from("project"));
    if table_element.is_none() {
        return;
    }
    let table = &mut table_element.unwrap().borrow_mut();
    expand_entry_points_inline_tables(table);
    for_entries(table, &mut |key, entry| match key.split('.').next().unwrap() {
        "name" => {
            update_string(entry, get_canonic_requirement_name);
        }
        "version" | "readme" | "license-files" | "scripts" | "entry-points" | "gui-scripts" => {
            update_string(entry, |s| String::from(s));
        }
        "authors" | "maintainers" => {}
        "license" => {}
        "description" => {
            update_string(entry, |s| {
                s.trim()
                    .lines()
                    .map(|part| {
                        part.trim()
                            .split(char::is_whitespace)
                            .filter(|part| !part.trim().is_empty())
                            .collect::<Vec<&str>>()
                            .join(" ")
                            .replace(" .", ".")
                    })
                    .collect::<Vec<String>>()
                    .join(" ")
            });
        }
        "requires-python" => {
            update_string(entry, |s| s.split_whitespace().collect());
        }
        "dependencies" | "optional-dependencies" => {
            transform_array(entry, &|s| format_requirement(s, keep_full_version));
            sort_array(entry, |e| get_canonic_requirement_name(e).to_lowercase());
        }
        "dynamic" | "keywords" => {
            transform_array(entry, &|s| String::from(s));
            sort_array(entry, |e| e.to_lowercase());
        }
        "classifiers" => {
            transform_array(entry, &|s| String::from(s));
            sort_array(entry, |e| e.to_lowercase());
        }
        _ => {}
    });

    generate_classifiers(table, max_supported_python, min_supported_python);
    for_entries(table, &mut |key, entry| {
        if key.as_str() == "classifiers" {
            sort_array(entry, |e| e.to_lowercase());
        }
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

fn expand_entry_points_inline_tables(table: &mut RefMut<Vec<SyntaxElement>>) {
    let (mut to_insert, mut count, mut key) = (Vec::<SyntaxElement>::new(), 0, String::from(""));
    for s_table_entry in table.iter() {
        count += 1;
        if s_table_entry.kind() == SyntaxKind::ENTRY {
            let mut has_inline_table = false;
            for s_in_table in s_table_entry.as_node().unwrap().children_with_tokens() {
                if s_in_table.kind() == SyntaxKind::KEY {
                    key = s_in_table.as_node().unwrap().text().to_string().trim().to_string();
                } else if key.starts_with("entry-points.") && s_in_table.kind() == SyntaxKind::VALUE {
                    for s_in_value in s_in_table.as_node().unwrap().children_with_tokens() {
                        if s_in_value.kind() == SyntaxKind::INLINE_TABLE {
                            has_inline_table = true;
                            for s_in_inline_table in s_in_value.as_node().unwrap().children_with_tokens() {
                                if s_in_inline_table.kind() == SyntaxKind::ENTRY {
                                    let mut with_key = String::from("");
                                    for s_in_entry in s_in_inline_table.as_node().unwrap().children_with_tokens() {
                                        if s_in_entry.kind() == SyntaxKind::KEY {
                                            for s_in_key in s_in_entry.as_node().unwrap().children_with_tokens() {
                                                if s_in_key.kind() == SyntaxKind::IDENT {
                                                    with_key = load_text(
                                                        s_in_key.as_token().unwrap().text(),
                                                        SyntaxKind::IDENT,
                                                    );
                                                    with_key = String::from(with_key.strip_quotes());
                                                    break;
                                                }
                                            }
                                        } else if s_in_entry.kind() == SyntaxKind::VALUE {
                                            for s_in_b_value in s_in_entry.as_node().unwrap().children_with_tokens() {
                                                if s_in_b_value.kind() == SyntaxKind::STRING {
                                                    let value = load_text(
                                                        s_in_b_value.as_token().unwrap().text(),
                                                        SyntaxKind::STRING,
                                                    );
                                                    if to_insert.last().unwrap().kind() != SyntaxKind::NEWLINE {
                                                        to_insert.push(create_newline());
                                                    }
                                                    let new_key = format!("{}.{}", key, with_key);
                                                    let got = create_entry_of_string(&new_key, &value);
                                                    to_insert.push(got);
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            if !has_inline_table {
                to_insert.push(s_table_entry.clone());
            }
        } else {
            to_insert.push(s_table_entry.clone());
        }
    }
    table.splice(0..count, to_insert);
}

fn generate_classifiers(
    table: &mut RefMut<Vec<SyntaxElement>>,
    max_supported_python: (u8, u8),
    min_supported_python: (u8, u8),
) {
    let (min, max, omit, classifiers) =
        get_python_requires_with_classifier(table, max_supported_python, min_supported_python);
    match classifiers {
        None => {
            let entry = create_array("classifiers");
            generate_classifiers_to_entry(entry.as_node().unwrap(), min, max, omit, HashSet::new());
            table.push(entry);
        }
        Some(c) => {
            let mut key_value = String::new();
            for table_row in table.iter() {
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
                                if array_entry_value.kind() == SyntaxKind::STRING {
                                    let txt =
                                        load_text(array_entry_value.as_token().unwrap().text(), SyntaxKind::STRING);
                                    delete_mode = delete.contains(&txt);
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
    table: &RefMut<Vec<SyntaxElement>>,
    max_supported_python: (u8, u8),
    min_supported_python: (u8, u8),
) -> MaxMinPythonWithClassifier {
    let mut classifiers: Option<HashSet<String>> = None;
    let mut mins: Vec<u8> = vec![];
    let mut maxs: Vec<u8> = vec![];
    let mut omit: Vec<u8> = vec![];
    assert_eq!(max_supported_python.0, 3, "for now only Python 3 supported");
    assert_eq!(min_supported_python.0, 3, "for now only Python 3 supported");

    for_entries(table, &mut |key, entry| {
        if key == "requires-python" {
            for child in entry.children_with_tokens() {
                if child.kind() == SyntaxKind::STRING {
                    let found_str_value = load_text(child.as_token().unwrap().text(), SyntaxKind::STRING);
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
                                if value.kind() == SyntaxKind::STRING {
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
    let min_py = (3, *mins.iter().max().unwrap_or(&min_supported_python.1));
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
        let count = root_ast.children_with_tokens().count();
        let mut tables = Tables::from_ast(&mut root_ast);
        fix_project(&mut tables, keep_full_version, max_supported_python, (3, 8));
        let entries = tables
            .table_set
            .iter()
            .flat_map(|e| e.borrow().clone())
            .collect::<Vec<SyntaxElement>>();
        root_ast.splice_children(0..count, entries);
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
    requires-python = ">=3.8"
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
    requires-python = ">3.7"
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
    requires-python = "==3.12"
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
    requires-python = ">3.6"
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
    #[case::project_description_whitespace(
        "[project]\ndescription = ' A  magic stuff \t is great\t\t.\r\n  Like  really  .\t\'\nrequires-python = '==3.12'",
        indoc ! {r#"
    [project]
    description = "A magic stuff is great. Like really."
    requires-python = "==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    "#},
        true,
        (3, 12),
    )]
    #[case::project_description_multiline(
        indoc ! {r#"
    [project]
    requires-python = "==3.12"
    description = """
    A magic stuff is great.
        Like really.
    """
    "#},
        indoc ! {r#"
    [project]
    description = "A magic stuff is great. Like really."
    requires-python = "==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    "#},
        true,
        (3, 12),
    )]
    #[case::project_dependencies_with_double_quotes(
        indoc ! {r#"
    [project]
    dependencies = [
        'packaging>=20.0;python_version>"3.4"',
        "appdirs"
    ]
    requires-python = "==3.12"
    "#},
        indoc ! {r#"
    [project]
    requires-python = "==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    dependencies = [
      "appdirs",
      "packaging>=20.0; python_version > \"3.4\"",
    ]
    "#},
        true,
        (3, 12),
    )]
    #[case::project_opt_inline_dependencies(
        indoc ! {r#"
    [project]
    dependencies = ["packaging>=24"]
    optional-dependencies.test = ["pytest>=8.1.1",  "covdefaults>=2.3"]
    optional-dependencies.docs = ["sphinx-argparse-cli>=1.15", "Sphinx>=7.3.7"]
    requires-python = "==3.12"
    "#},
        indoc ! {r#"
    [project]
    requires-python = "==3.12"
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.12",
    ]
    dependencies = [
      "packaging>=24",
    ]
    optional-dependencies.docs = [
      "sphinx>=7.3.7",
      "sphinx-argparse-cli>=1.15",
    ]
    optional-dependencies.test = [
      "covdefaults>=2.3",
      "pytest>=8.1.1",
    ]
    "#},
        true,
        (3, 12),
    )]
    #[case::project_opt_dependencies(
        indoc ! {r#"
    [project.optional-dependencies]
    test = ["pytest>=8.1.1",  "covdefaults>=2.3"]
    docs = ["sphinx-argparse-cli>=1.15", "Sphinx>=7.3.7"]
    "#},
        indoc ! {r#"
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    optional-dependencies.docs = [
      "sphinx>=7.3.7",
      "sphinx-argparse-cli>=1.15",
    ]
    optional-dependencies.test = [
      "covdefaults>=2.3",
      "pytest>=8.1.1",
    ]
    "#},
        true,
        (3, 8),
    )]
    #[case::project_scritps_collapse(
        indoc ! {r#"
    [project.scripts]
    c = 'd'
    a = "b"
    "#},
        indoc ! {r#"
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    scripts.a = "b"
    scripts.c = "d"
    "#},
        true,
        (3, 8),
    )]
    #[case::project_entry_points_collapse(
        indoc ! {r#"
    [project]
    entry-points.tox = {"tox-uv" = "tox_uv.plugin", "tox" = "tox.plugin"}
    [project.scripts]
    virtualenv = "virtualenv.__main__:run_with_catch"
    [project.gui-scripts]
    hello-world = "timmins:hello_world"
    [project.entry-points."virtualenv.activate"]
    bash = "virtualenv.activation.bash:BashActivator"
    [project.entry-points]
    B = {base = "vehicle_crash_prevention.main:VehicleBase"}
    [project.entry-points."no_crashes.vehicle"]
    base = "vehicle_crash_prevention.main:VehicleBase"
    [project.entry-points.plugin-namespace]
    plugin-name1 = "pkg.subpkg1"
    plugin-name2 = "pkg.subpkg2:func"
    "#},
        indoc ! {r#"
    [project]
    classifiers = [
      "Programming Language :: Python :: 3 :: Only",
      "Programming Language :: Python :: 3.8",
    ]
    scripts.virtualenv = "virtualenv.__main__:run_with_catch"
    gui-scripts.hello-world = "timmins:hello_world"
    entry-points.B.base = "vehicle_crash_prevention.main:VehicleBase"
    entry-points."no_crashes.vehicle".base = "vehicle_crash_prevention.main:VehicleBase"
    entry-points.plugin-namespace.plugin-name1 = "pkg.subpkg1"
    entry-points.plugin-namespace.plugin-name2 = "pkg.subpkg2:func"
    entry-points.tox.tox = "tox.plugin"
    entry-points.tox.tox-uv = "tox_uv.plugin"
    entry-points."virtualenv.activate".bash = "virtualenv.activation.bash:BashActivator"
    "#},
        true,
        (3, 8),
    )]
    fn test_format_project(
        #[case] start: &str,
        #[case] expected: &str,
        #[case] keep_full_version: bool,
        #[case] max_supported_python: (u8, u8),
    ) {
        assert_eq!(evaluate(start, keep_full_version, max_supported_python), expected);
    }
}

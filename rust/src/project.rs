use taplo::syntax::{SyntaxElement, SyntaxKind};

use crate::helpers::array::{array_pep508_normalize, sort_array};
use crate::helpers::pep508::req_name;
use crate::helpers::table::{for_entries, reorder_table_keys};

pub fn fix_project(table: &mut Vec<SyntaxElement>, keep_full_version: bool, max_supported_python: (u8, u8)) {
    let (min_supported_py, max_supported_py) = get_python_requires(table, max_supported_python);
    for_entries(table, &mut |key, entry| {
        if key == "dependencies" {
            array_pep508_normalize(entry, keep_full_version);
            sort_array(entry, |e| req_name(e.as_str()).to_lowercase());
        }
    });
    println!("{:?} {:?}", min_supported_py, max_supported_py);
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

fn get_python_requires(table: &mut Vec<SyntaxElement>, max_supported_python: (u8, u8)) -> ((u8, u8), (u8, u8)) {
    let mut min_py = (3, 8);
    let mut max_py = max_supported_python;
    for_entries(table, &mut |key, entry| {
        if key == "requires-python" {
            for child in entry.children_with_tokens() {
                if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&child.kind()) {
                    let found = child.as_token().unwrap().text();
                    let found_str_value: String = found[1..found.len() - 1].split_whitespace().collect();
                    if found_str_value.starts_with(">3.") {
                        min_py.1 = found_str_value
                            .strip_prefix(">3.")
                            .unwrap()
                            .parse::<u8>()
                            .unwrap_or(min_py.1 - 1)
                            + 1;
                    } else if found_str_value.starts_with(">=3.") {
                        min_py.1 = found_str_value
                            .strip_prefix(">=3.")
                            .unwrap()
                            .parse::<u8>()
                            .unwrap_or(min_py.1);
                    } else if found_str_value.starts_with("==3.") {
                        min_py.1 = found_str_value
                            .strip_prefix("==3.")
                            .unwrap()
                            .parse::<u8>()
                            .unwrap_or(min_py.1);
                        max_py = min_py;
                    }
                }
            }
        }
    });
    (min_py, max_py)
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
        format_syntax(root_ast, Options::default())
    }

    #[rstest]
    #[case::no_project(
    indoc ! {r#""#},
    "\n",
    false,
    (3, 12),
    )]
    #[case::project_requires_no_keep(
    indoc ! {r#"
    [project]
    dependencies=["a>=1.0.0", "b.c>=1.5.0"]
    "#},
    indoc ! {r#"
    [project]
    dependencies = ["a>=1", "b.c>=1.5"]
    "#},
    false,
    (3, 12),
    )]
    #[case::project_requires_keep(
    indoc ! {r#"
    [project]
    dependencies=["a>=1.0.0", "b.c>=1.5.0"]
    "#},
    indoc ! {r#"
    [project]
    dependencies = ["a>=1.0.0", "b.c>=1.5.0"]
    "#},
    true,
    (3, 12),
    )]
    #[case::project_requires_ge(
    indoc ! {r#"
    [project]
    requires-python = " >= 3.7"
    "#},
    indoc ! {r#"
    [project]
    requires-python = " >= 3.7"
    "#},
    true,
    (3, 11),
    )]
    #[case::project_requires_gt(
    indoc ! {r#"
    [project]
    requires-python = " > 3.7"
    "#},
    indoc ! {r#"
    [project]
    requires-python = " > 3.7"
    "#},
    true,
    (3, 11),
    )]
    #[case::project_requires_eq(
    indoc ! {r#"
    [project]
    requires-python = " == 3.12"
    "#},
    indoc ! {r#"
    [project]
    requires-python = " == 3.12"
    "#},
    true,
    (3, 11),
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

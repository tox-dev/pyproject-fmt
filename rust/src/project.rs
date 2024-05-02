use taplo::syntax::{SyntaxElement, SyntaxKind};

use crate::common::{for_entries, reorder_table_keys};

pub fn fix_project(table: &mut Vec<SyntaxElement>, keep_full_version: bool, max_supported_python: (u8, u8)) {
    let min_supported_python = get_python_requires(table);
    for_entries(table, &mut |key, entry| {
        if key == "dependencies" {
            crate::pep503::normalize_array_entry(entry, keep_full_version);
        }
    });
    println!("{:?} {:?}", max_supported_python, min_supported_python);
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

fn get_python_requires(table: &mut Vec<SyntaxElement>) -> (u8, u8) {
    let mut min_python_requires = 8;
    for_entries(table, &mut |key, entry| {
        if key == "requires-python" {
            for child in entry.children_with_tokens() {
                if [SyntaxKind::STRING, SyntaxKind::STRING_LITERAL].contains(&child.kind()) {
                    let found = child.as_token().unwrap().text();
                    let found_str_value: String = found[1..found.len() - 1].split_whitespace().collect();
                    if found_str_value.starts_with(">3.") {
                        min_python_requires = found_str_value
                            .strip_prefix(">3.")
                            .unwrap()
                            .parse::<u8>()
                            .unwrap_or(min_python_requires - 1)
                            + 1;
                    } else if found_str_value.starts_with(">=3.") {
                        min_python_requires = found_str_value
                            .strip_prefix(">=3.")
                            .unwrap()
                            .parse::<u8>()
                            .unwrap_or(min_python_requires);
                    }
                }
            }
        }
    });
    (3, min_python_requires)
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;
    use taplo::syntax::SyntaxElement;

    use crate::project::fix_project;

    fn evaluate(start: &str, keep_full_version: bool, max_supported_python: (u8, u8)) -> String {
        let mut root_ast = parse(start).into_syntax().clone_for_update();
        let mut tables = crate::common::Tables::from_ast(&mut root_ast);
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
    // #[case::no_project(
    // indoc ! {r#""#},
    // "\n",
    // false,
    // (3, 12),
    // )]
    // #[case::project_requires_no_keep(
    // indoc ! {r#"
    // [project]
    // dependencies=["a>=1.0.0", "b.c>=1.5.0"]
    // "#},
    // indoc ! {r#"
    // [project]
    // dependencies = ["a>=1", "b.c>=1.5"]
    // "#},
    // false,
    // (3, 12),
    // )]
    // #[case::project_requires_keep(
    // indoc ! {r#"
    // [project]
    // dependencies=["a>=1.0.0", "b.c>=1.5.0"]
    // "#},
    // indoc ! {r#"
    // [project]
    // dependencies = ["a>=1.0.0", "b.c>=1.5.0"]
    // "#},
    // true,
    // (3, 12),
    // )]
    #[case::project_requires_keep(
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
    fn test_normalize_requirement(
        #[case] start: &str,
        #[case] expected: &str,
        #[case] keep_full_version: bool,
        #[case] max_supported_python: (u8, u8),
    ) {
        assert_eq!(evaluate(start, keep_full_version, max_supported_python), expected);
    }
}

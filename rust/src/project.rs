use taplo::syntax::{SyntaxElement, SyntaxKind};

pub fn fix_project(table: SyntaxElement, keep_full_version: bool, max_supported_python: (u8, u8)) {
    let mut key = String::new();
    for table_entry in table.as_node().unwrap().children_with_tokens() {
        if table_entry.kind() == SyntaxKind::KEY {
            key = table_entry.as_node().unwrap().text().to_string().trim().to_string();
        } else if table_entry.kind() == SyntaxKind::VALUE {
            if key == "dependencies" {
                for table_value in table_entry.as_node().unwrap().children_with_tokens() {
                    if table_value.kind() == SyntaxKind::ARRAY {
                        crate::pep503::normalize_array(table_value, keep_full_version);
                    }
                }
            } else if key == "name" {
            }
        }
    }
    println!("{:?}", max_supported_python);
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use pretty_assertions::assert_eq;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;
    use taplo::syntax::SyntaxKind;

    use crate::common::get_table_name;
    use crate::project::fix_project;

    fn evaluate(start: &str, keep_full_version: bool, max_supported_python: (u8, u8)) -> String {
        let root_ast = parse(start).into_syntax().clone_for_update();
        let mut table_name = String::new();
        for children in root_ast.children_with_tokens() {
            if children.kind() == SyntaxKind::TABLE_HEADER {
                table_name = get_table_name(&children);
            } else if children.kind() == SyntaxKind::ENTRY && table_name == "project" {
                fix_project(children, keep_full_version, max_supported_python);
            }
        }
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
    fn test_normalize_requirement(
        #[case] start: &str,
        #[case] expected: &str,
        #[case] keep_full_version: bool,
        #[case] max_supported_python: (u8, u8),
    ) {
        assert_eq!(evaluate(start, keep_full_version, max_supported_python), expected);
    }
}

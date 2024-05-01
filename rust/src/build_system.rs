use taplo::syntax::{SyntaxElement, SyntaxKind};

pub fn fix_build_system(table: SyntaxElement, keep_full_version: bool) {
    let mut key = String::new();
    for table_entry in table.as_node().unwrap().children_with_tokens() {
        if table_entry.kind() == SyntaxKind::KEY {
            key = table_entry.as_node().unwrap().text().to_string().trim().to_string();
        } else if table_entry.kind() == SyntaxKind::VALUE {
            if key == "requires" {
                for table_value in table_entry.as_node().unwrap().children_with_tokens() {
                    if table_value.kind() == SyntaxKind::ARRAY {
                        crate::pep503::normalize_array(table_value, keep_full_version);
                    }
                }
            } else if key == "build-backend" {
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;
    use taplo::syntax::SyntaxKind;

    use crate::build_system::fix_build_system;
    use crate::common::get_table_name;

    fn evaluate(start: &str, keep_full_version: bool) -> String {
        let root_ast = parse(start).into_syntax().clone_for_update();
        let mut table_name = String::new();
        for children in root_ast.children_with_tokens() {
            if children.kind() == SyntaxKind::TABLE_HEADER {
                table_name = get_table_name(&children);
            } else if children.kind() == SyntaxKind::ENTRY && table_name == "build-system" {
                fix_build_system(children, keep_full_version);
            }
        }
        format_syntax(root_ast, Options::default())
    }

    #[rstest]
    #[case::no_build_system(
    indoc ! {r#""#},
    "\n",
    false
    )]
    #[case::build_system_requires_no_keep(
    indoc ! {r#"
    [build-system]
    requires=["a>=1.0.0", "b.c>=1.5.0"]
    "#},
    indoc ! {r#"
    [build-system]
    requires = ["a>=1", "b.c>=1.5"]
    "#},
    false
    )]
    #[case::build_system_requires_keep(
    indoc ! {r#"
    [build-system]
    requires=["a>=1.0.0", "b.c>=1.5.0"]
    "#},
    indoc ! {r#"
    [build-system]
    requires = ["a>=1.0.0", "b.c>=1.5.0"]
    "#},
    true
    )]
    fn test_normalize_requirement(#[case] start: &str, #[case] expected: &str, #[case] keep_full_version: bool) {
        assert_eq!(evaluate(start, keep_full_version), expected);
    }
}

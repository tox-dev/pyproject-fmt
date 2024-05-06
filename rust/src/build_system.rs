use taplo::syntax::SyntaxElement;

use crate::helpers::array::array_pep508_normalize;
use crate::helpers::table::{for_entries, reorder_table_keys};

pub fn fix_build_system(table: &mut Vec<SyntaxElement>, keep_full_version: bool) {
    for_entries(table, &mut |key, entry| {
        if key == "requires" {
            array_pep508_normalize(entry, keep_full_version);
        }
    });
    reorder_table_keys(table, &["", "build-backend", "requires", "backend-path"]);
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;
    use taplo::syntax::SyntaxElement;

    use crate::build_system::fix_build_system;
    use crate::helpers::table::Tables;

    fn evaluate(start: &str, keep_full_version: bool) -> String {
        let mut root_ast = parse(start).into_syntax().clone_for_update();
        let mut tables = Tables::from_ast(&mut root_ast);
        match tables.get(&String::from("build-system")) {
            None => {}
            Some(t) => {
                fix_build_system(t, keep_full_version);
            }
        }
        let entries = tables.table_set.into_iter().flatten().collect::<Vec<SyntaxElement>>();
        root_ast.splice_children(0..entries.len(), entries);
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
    #[case::build_system_order(
    indoc ! {r#"
    [build-system]
    # more
    more = true # more post
    #  extra
    extra = 1 # extra post
    # path
    backend-path = ['A'] # path post
    # requires
    requires = ["B"] # requires post
    # backend
    build-backend = "hatchling.build" # backend post
    # post
    "#},
    indoc ! {r#"
    [build-system]
    # more
    build-backend = "hatchling.build" # backend post
    # post
    requires = ["B"] # requires post
    # backend
    backend-path = ['A'] # path post
    # requires
    more = true # more post
    #  extra
    extra = 1 # extra post
    # path
    "#},
    true
    )]
    fn test_normalize_requirement(#[case] start: &str, #[case] expected: &str, #[case] keep_full_version: bool) {
        assert_eq!(evaluate(start, keep_full_version), expected);
    }
}

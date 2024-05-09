use crate::helpers::array::{sort, transform};
use crate::helpers::pep508::{format_requirement, get_canonic_requirement_name};
use crate::helpers::table::{for_entries, reorder_table_keys, Tables};

pub fn fix_build(tables: &mut Tables, keep_full_version: bool) {
    let table_element = tables.get(&String::from("build-system"));
    if table_element.is_none() {
        return;
    }
    let table = &mut table_element.unwrap().borrow_mut();
    for_entries(table, &mut |key, entry| match key.as_str() {
        "requires" => {
            transform(entry, &|s| format_requirement(s, keep_full_version));
            sort(entry, |e| get_canonic_requirement_name(e).to_lowercase());
        }
        "backend-path" => {
            sort(entry, str::to_lowercase);
        }
        _ => {}
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

    use crate::build_system::fix_build;
    use crate::helpers::table::Tables;

    fn evaluate(start: &str, keep_full_version: bool) -> String {
        let root_ast = parse(start).into_syntax().clone_for_update();
        let count = root_ast.children_with_tokens().count();
        let mut tables = Tables::from_ast(&root_ast);
        fix_build(&mut tables, keep_full_version);
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
    #[case::no_build_system(
        indoc ! {r""},
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
    requires = [
      "a>=1",
      "b-c>=1.5",
    ]
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
    requires = [
      "a>=1.0.0",
      "b-c>=1.5.0",
    ]
    "#},
        true
    )]
    // #[case::build_system_order(
    // indoc ! {r#"
    // [build-system]
    // # more
    // more = true # more post
    // #  extra
    // extra = 1 # extra post
    // # path
    // backend-path = ['A'] # path post
    // # requires
    // requires = ["B"] # requires post
    // # backend
    // build-backend = "hatchling.build" # backend post
    // # post
    // "#},
    // indoc ! {r#"
    // [build-system]
    // # more
    // build-backend = "hatchling.build" # backend post
    // # post
    // requires = ["b"] # requires post
    // # backend
    // backend-path = ['A'] # path post
    // # requires
    // more = true # more post
    // #  extra
    // extra = 1 # extra post
    // # path
    // "#},
    // true
    // )]
    fn test_normalize_requirement(#[case] start: &str, #[case] expected: &str, #[case] keep_full_version: bool) {
        assert_eq!(evaluate(start, keep_full_version), expected);
    }
}

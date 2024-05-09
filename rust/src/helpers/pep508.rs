use pyo3::prelude::*;
use pyo3::prepare_freethreaded_python;
use pyo3::types::IntoPyDict;

pub fn format_requirement(value: &str, keep_full_version: bool) -> String {
    prepare_freethreaded_python();
    Python::with_gil(|py| {
        let norm: String = PyModule::import_bound(py, "pyproject_fmt._pep508")?
            .getattr("normalize_req")?
            .call(
                (value,),
                Some(&[("keep_full_version", keep_full_version)].into_py_dict_bound(py)),
            )?
            .extract()?;
        Ok::<String, PyErr>(norm)
    })
    .unwrap()
}

pub fn get_canonic_requirement_name(value: &str) -> String {
    prepare_freethreaded_python();
    Python::with_gil(|py| {
        let norm: String = PyModule::import_bound(py, "pyproject_fmt._pep508")?
            .getattr("req_name")?
            .call1((value,))?
            .extract()?;
        Ok::<String, PyErr>(norm)
    })
    .unwrap()
}

#[cfg(test)]
mod tests {
    use indoc::indoc;
    use rstest::rstest;
    use taplo::formatter::{format_syntax, Options};
    use taplo::parser::parse;

    use crate::global::reorder_tables;
    use crate::helpers::table::Tables;

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
        let root_ast = parse(start).into_syntax().clone_for_update();
        let mut tables = Tables::from_ast(&root_ast);
        reorder_tables(&root_ast, &mut tables);
        let got = format_syntax(root_ast, Options::default());
        assert_eq!(got, expected);
    }
}

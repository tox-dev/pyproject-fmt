use taplo::rowan::SyntaxNode;
use taplo::syntax::Lang;

use crate::helpers::table::Tables;

pub fn reorder_tables(root_ast: &SyntaxNode<Lang>, tables: &mut Tables) {
    tables.reorder(
        root_ast,
        &[
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
        ],
    );
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
    requires = [
      "c",
      "d",
    ]

    [project]
    name = "alpha"
    dependencies = [
      "e",
    ]

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
        let opt = Options {
            column_width: 1,
            ..Options::default()
        };
        let got = format_syntax(root_ast, opt);
        assert_eq!(got, expected);
    }
}

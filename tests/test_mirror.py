from __future__ import annotations

import os
import sys
from pathlib import Path
from subprocess import call, check_call, check_output
from textwrap import dedent

import pytest


@pytest.fixture(scope="session")
def root() -> Path:
    return Path(__file__).parents[1]


def test_last_tag(tmp_path: Path, root: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # test this project against its latest tag
    ver = check_output(["git", "describe", "--tags", "--abbrev=0"], text=True).strip()
    print(f"Using version {ver}")  # noqa: T201

    pre_commit_home = tmp_path / "h"
    pre_commit_home.mkdir()
    monkeypatch.setenv("PRE_COMMIT_HOME", str(pre_commit_home))

    project = tmp_path / "p"
    project.mkdir()
    monkeypatch.chdir(project)
    (project / ".pre-commit-config.yaml").write_text(
        dedent(f"""
        repos:
          - repo: file://{root}
            rev: "{ver}"
            hooks:
              - id: pyproject-fmt
                language_version: {sys.executable}
    """)
    )
    toml = project / "pyproject.toml"
    toml.write_text("[project]\nrequires-python='>=3.13'")

    if os.environ.get("GITHUB_ACTIONS"):  # pragma: no branch
        check_call(["git", "config", "--global", "init.defaultBranch", "main"])  # pragma: no cover
        check_call(["git", "config", "--global", "user.email", "e@a.com"])  # pragma: no cover
        check_call(["git", "config", "--global", "user.name", "A B"])  # pragma: no cover

    check_call(["git", "init"])
    check_call(["git", "add", "."])
    check_call(["git", "commit", "-m", "Initial commit"])
    check_call(["ls", "-alth"])

    pre_commit = Path(sys.executable).parent / "pre-commit"

    check_call([pre_commit, "install-hooks"])
    assert list(pre_commit_home.iterdir())

    code = call([pre_commit, "run", "--all-files"])
    assert code == 1

    assert toml.read_text().splitlines() == [
        "[project]",
        'requires-python = ">=3.13"',
        'classifiers = [ "Programming Language :: Python :: 3 :: Only", "Programming Language :: Python :: 3.13" ]',
    ]

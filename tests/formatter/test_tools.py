from __future__ import annotations

from pyproject_fmt.formatter.tools import fmt_tools
from tests import Fmt


def test_tools_ordering(fmt: Fmt) -> None:
    content = """
    [tool.coverage]
    a = 0
    [tool.pytest]
    a = 0
    [tool.black]
    a = 0
    [tool.isort]
    a = 0
    [tool.flake8]
    [tool.hatch]
    a = 0
    [tool.setuptools_scm]
    a = 0
    [tool.setuptools]
    a.b = 0

    """
    expected = """
    [tool.setuptools]
    a.b = 0

    [tool.setuptools_scm]
    a = 0

    [tool.hatch]
    a = 0

    [tool.black]
    a = 0

    [tool.isort]
    a = 0

    [tool.flake8]

    [tool.pytest]
    a = 0

    [tool.coverage]
    a = 0
        """
    fmt(fmt_tools, content, expected)

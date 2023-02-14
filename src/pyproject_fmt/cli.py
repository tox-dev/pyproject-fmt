from __future__ import annotations

import os
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)
from pathlib import Path
from typing import Sequence

from pyproject_fmt.formatter.config import DEFAULT_INDENT, Config


class PyProjectFmtNamespace(Namespace):
    """Options for pyproject-fmt tool"""

    inputs: list[Path]
    stdout: bool
    indent: int
    check: bool

    @property
    def configs(self) -> list[Config]:
        return [Config(toml, toml.read_text(encoding="utf-8"), self.indent) for toml in self.inputs]


def pyproject_toml_path_creator(argument: str) -> Path:
    """Validate that pyproject.toml can be formatted.

    :param argument: the string argument passed in
    :return: the pyproject.toml path
    """
    path = Path(argument).absolute()
    if path.is_dir():
        path = path / "pyproject.toml"
    if not path.exists():
        raise ArgumentTypeError("path does not exist")
    if not path.is_file():
        raise ArgumentTypeError("path is not a file")
    if not os.access(path, os.R_OK):
        raise ArgumentTypeError("cannot read path")  # pragma: no cover
    if not os.access(path, os.W_OK):
        raise ArgumentTypeError("cannot write path")  # pragma: no cover
    return path


def _build_cli() -> ArgumentParser:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    msg = "print the formatted text to the stdout (instead of update in-place)"
    group.add_argument("-s", "--stdout", action="store_true", help=msg)
    msg = "check and fail if any input would be formatted, printing any diffs"
    group.add_argument("--check", action="store_true", help=msg)
    parser.add_argument("--indent", type=int, default=DEFAULT_INDENT, help="number of spaces to indent")
    msg = "pyproject.toml file(s) to format"
    parser.add_argument("inputs", nargs="+", type=pyproject_toml_path_creator, help=msg)
    return parser


def cli_args(args: Sequence[str]) -> PyProjectFmtNamespace:
    """
    Load the tools options.

    :param args: CLI arguments
    :return: the parsed options
    """
    parser = _build_cli()
    return parser.parse_args(namespace=PyProjectFmtNamespace(), args=args)


__all__ = [
    "cli_args",
    "PyProjectFmtNamespace",
]

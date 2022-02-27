from __future__ import annotations

import os
from argparse import ArgumentParser, ArgumentTypeError, Namespace
from pathlib import Path
from typing import Sequence


class PyProjectFmtNamespace(Namespace):
    """Options for the ``pyproject_fmt`` library"""

    indent = 2
    """Number of indentation spaces used for formatting"""


class PyProjectFmtCliNamespace(PyProjectFmtNamespace):
    """Options for pyproject-fmt tool"""

    pyproject_toml: Path
    stdout: bool


def pyproject_toml_path_creator(argument: str) -> Path:
    """Validate that tox.ini can be formatted.

    :param argument: the string argument passed in
    :return: the tox.ini path
    """
    path = Path(argument).absolute()
    if not path.exists():
        raise ArgumentTypeError("path does not exists")
    if not path.is_file():
        raise ArgumentTypeError("path is not a file")
    if not os.access(path, os.R_OK):
        raise ArgumentTypeError("cannot read path")  # pragma: no cover
    if not os.access(path, os.W_OK):
        raise ArgumentTypeError("cannot write path")  # pragma: no cover
    return path


def _build_cli() -> ArgumentParser:
    parser = ArgumentParser()
    msg = "print the formatted text to the stdout (instead of update in-place)"
    parser.add_argument("-s", "--stdout", action="store_true", help=msg)
    parser.add_argument("pyproject_toml", type=pyproject_toml_path_creator, help="tox ini file to format")
    return parser


def cli_args(args: Sequence[str]) -> PyProjectFmtCliNamespace:
    """
    Load the tools options.

    :param args: CLI arguments
    :return: the parsed options
    """
    parser = _build_cli()
    return parser.parse_args(namespace=PyProjectFmtCliNamespace(), args=args)


__all__ = [
    "cli_args",
    "PyProjectFmtNamespace",
]

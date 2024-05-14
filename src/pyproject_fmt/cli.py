"""CLI interface parser."""

from __future__ import annotations

import os
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)
from dataclasses import dataclass
from functools import partial
from importlib.metadata import version
from pathlib import Path
from typing import Sequence

from pyproject_fmt._api import Settings


class PyProjectFmtNamespace(Namespace):
    """Options for pyproject-fmt tool."""

    inputs: list[Path]
    stdout: bool
    check: bool

    column_width: int
    indent: int
    keep_full_version: bool
    max_supported_python: tuple[int, int]


@dataclass(frozen=True)
class Config:
    """Configuration flags for the formatting."""

    pyproject_toml: Path
    stdout: bool  # push to standard out
    check: bool  # check only
    settings: Settings

    @property
    def toml(self) -> str:
        """:return: the toml files content"""
        return self.pyproject_toml.read_text(encoding="utf-8")


def pyproject_toml_path_creator(argument: str) -> Path:
    """
    Validate that pyproject.toml can be formatted.

    :param argument: the string argument passed in
    :return: the pyproject.toml path
    """
    path = Path(argument).absolute()
    if path.is_dir():
        path /= "pyproject.toml"
    if not path.exists():
        msg = "path does not exist"
        raise ArgumentTypeError(msg)
    if not path.is_file():
        msg = "path is not a file"
        raise ArgumentTypeError(msg)
    if not os.access(path, os.R_OK):
        msg = "cannot read path"
        raise ArgumentTypeError(msg)
    if not os.access(path, os.W_OK):
        msg = "cannot write path"
        raise ArgumentTypeError(msg)
    return path


def _build_cli() -> ArgumentParser:
    defaults = Settings()
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        prog="pyproject-fmt",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help="print package version of pyproject_fmt",
        version=f"%(prog)s ({version('pyproject-fmt')})",
    )
    group = parser.add_mutually_exclusive_group()
    msg = "print the formatted text to the stdout (instead of update in-place)"
    group.add_argument("-s", "--stdout", action="store_true", help=msg)
    msg = "check and fail if any input would be formatted, printing any diffs"
    group.add_argument("--check", action="store_true", help=msg)
    parser.add_argument(
        "--column-width",
        type=int,
        default=defaults.column_width,
        help="max column width in the file",
        metavar="count",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=defaults.indent,
        help="number of spaces to indent",
        metavar="count",
    )
    parser.add_argument(
        "--max-supported-python",
        metavar="minor.major",
        type=partial(Settings._version_argument, exc=ArgumentTypeError),  # noqa: SLF001
        default=defaults.max_supported_python,
        help="latest Python version the project supports (e.g. 3.13)",
    )
    msg = "keep full dependency versions - do not remove redundant .0 from versions"
    parser.add_argument("--keep-full-version", action="store_true", help=msg)
    msg = "pyproject.toml file(s) to format"
    parser.add_argument("inputs", nargs="+", type=pyproject_toml_path_creator, help=msg)
    return parser


def cli_args(args: Sequence[str]) -> list[Config]:
    """
    Load the tools options.

    :param args: CLI arguments
    :return: the parsed options
    """
    parser = _build_cli()
    opt = PyProjectFmtNamespace()
    parser.parse_args(namespace=opt, args=args)
    settings = Settings(
        column_width=opt.column_width,
        indent=opt.indent,
        keep_full_version=opt.keep_full_version,
        max_supported_python=opt.max_supported_python,
    )
    return [
        Config(
            pyproject_toml=pyproject_toml,
            stdout=opt.stdout,
            check=opt.check,
            settings=settings,
        )
        for pyproject_toml in opt.inputs
    ]


__all__ = [
    "Config",
    "PyProjectFmtNamespace",
    "cli_args",
]

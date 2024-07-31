"""CLI interface parser."""

from __future__ import annotations

import os
import sys
from argparse import (
    ArgumentDefaultsHelpFormatter,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
)
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path
from typing import Sequence

from pyproject_fmt_rust import Settings

if sys.version_info >= (3, 11):  # pragma: >=3.11 cover
    import tomllib
else:  # pragma: <3.11 cover
    import tomli as tomllib


class PyProjectFmtNamespace(Namespace):
    """Options for pyproject-fmt tool."""

    inputs: list[Path]
    stdout: bool
    check: bool
    no_print_diff: bool

    column_width: int
    indent: int
    keep_full_version: bool
    max_supported_python: tuple[int, int]


@dataclass(frozen=True)
class Config:
    """Configuration flags for the formatting."""

    pyproject_toml: Path | None  # path to the toml file or None if stdin
    toml: str  # the toml file content
    stdout: bool  # push to standard out, implied if reading from stdin
    check: bool  # check only
    no_print_diff: bool  # don't print diff
    settings: Settings


def pyproject_toml_path_creator(argument: str) -> Path | None:
    """
    Validate that pyproject.toml can be formatted.

    :param argument: the string argument passed in
    :return: the pyproject.toml path or None if stdin
    :raises ArgumentTypeError: invalid argument
    """
    if argument == "-":
        return None  # stdin, no further validation needed
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


def _version_argument(got: str) -> tuple[int, int]:
    parts = got.split(".")
    if len(parts) != 2:  # noqa: PLR2004
        msg = f"invalid version: {got}, must be e.g. 3.12"
        raise ArgumentTypeError(msg)
    try:
        return int(parts[0]), int(parts[1])
    except ValueError as exc:
        msg = f"invalid version: {got} due {exc!r}, must be e.g. 3.12"
        raise ArgumentTypeError(msg) from exc


def _build_cli() -> ArgumentParser:
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

    mode_group = parser.add_argument_group("run mode")
    mode = mode_group.add_mutually_exclusive_group()
    msg = "print the formatted TOML to the stdout, implied if reading from stdin"
    mode.add_argument("-s", "--stdout", action="store_true", help=msg)
    msg = "check and fail if any input would be formatted, printing any diffs"
    mode.add_argument("--check", action="store_true", help=msg)
    mode_group.add_argument(
        "-n",
        "--no-print-diff",
        action="store_true",
        help="Flag indicating to print diff for the check mode",
    )

    format_group = parser.add_argument_group("formatting behavior")
    format_group.add_argument(
        "--column-width",
        type=int,
        default=120,
        help="max column width in the TOML file",
        metavar="count",
    )
    format_group.add_argument(
        "--indent",
        type=int,
        default=2,
        help="number of spaces to use for indentation",
        metavar="count",
    )
    msg = "keep full dependency versions - do not remove redundant .0 from versions"
    format_group.add_argument("--keep-full-version", action="store_true", help=msg)
    format_group.add_argument(
        "--max-supported-python",
        metavar="minor.major",
        type=_version_argument,
        default=(3, 12),
        help="latest Python version the project supports (e.g. 3.13)",
    )

    msg = "pyproject.toml file(s) to format, use '-' to read from stdin"
    parser.add_argument(
        "inputs",
        nargs="+",
        type=pyproject_toml_path_creator,
        help=msg,
    )
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
    res = []
    for pyproject_toml in opt.inputs:
        column_width = opt.column_width
        indent = opt.indent
        keep_full_version = opt.keep_full_version
        max_supported_python = opt.max_supported_python
        raw_pyproject_toml = sys.stdin.read() if pyproject_toml is None else pyproject_toml.read_text(encoding="utf-8")
        config = tomllib.loads(raw_pyproject_toml)
        if "tool" in config and "pyproject-fmt" in config["tool"]:
            for key, entry in config["tool"]["pyproject-fmt"].items():
                if key == "column_width":
                    column_width = int(entry)
                elif key == "indent":
                    indent = int(entry)
                elif key == "keep_full_version":
                    keep_full_version = bool(entry)
                elif key == "max_supported_python":
                    max_supported_python = _version_argument(entry)
        res.append(
            Config(
                pyproject_toml=pyproject_toml,
                toml=raw_pyproject_toml,
                stdout=opt.stdout,
                check=opt.check,
                no_print_diff=opt.no_print_diff,
                settings=Settings(
                    column_width=column_width,
                    indent=indent,
                    keep_full_version=keep_full_version,
                    max_supported_python=max_supported_python,
                    min_supported_python=(3, 8),  # default for when the user did not specify via requires-python
                ),
            )
        )

    return res


__all__ = [
    "Config",
    "PyProjectFmtNamespace",
    "cli_args",
]

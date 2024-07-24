"""Main entry point for the formatter."""

from __future__ import annotations

import difflib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, Sequence

from pyproject_fmt_rust import format_toml

from pyproject_fmt.cli import cli_args

if TYPE_CHECKING:
    from pyproject_fmt.cli import Config

GREEN = "\u001b[32m"
RED = "\u001b[31m"
RESET = "\u001b[0m"


def color_diff(diff: Iterable[str]) -> Iterable[str]:
    """
    Visualize difference with colors.

    :param diff: the diff lines
    """
    for line in diff:
        if line.startswith("+"):
            yield f"{GREEN}{line}{RESET}"
        elif line.startswith("-"):
            yield f"{RED}{line}{RESET}"
        else:
            yield line


def _handle_one(config: Config) -> bool:
    formatted = format_toml(config.toml, config.settings)
    before = config.toml
    changed = before != formatted
    if config.pyproject_toml is None or config.stdout:  # when reading from stdin or writing to stdout, print new format
        print(formatted, end="")  # noqa: T201
        return changed

    if before != formatted and not config.check:
        config.pyproject_toml.write_text(formatted, encoding="utf-8")
    if config.no_print_diff:
        return changed
    try:
        name = str(config.pyproject_toml.relative_to(Path.cwd()))
    except ValueError:
        name = str(config.pyproject_toml)
    diff: Iterable[str] = []
    if changed:
        diff = difflib.unified_diff(before.splitlines(), formatted.splitlines(), fromfile=name, tofile=name)

    if diff:
        diff = color_diff(diff)
        print("\n".join(diff))  # print diff on change  # noqa: T201
    else:
        print(f"no change for {name}")  # noqa: T201
    return changed


def run(args: Sequence[str] | None = None) -> int:
    """
    Run the formatter.

    :param args: command line arguments, by default use sys.argv[1:]
    :return: exit code - 0 means already formatted correctly, otherwise 1
    """
    configs = cli_args(sys.argv[1:] if args is None else args)
    results = [_handle_one(config) for config in configs]
    return 1 if any(results) else 0  # exit with non success on change


if __name__ == "__main__":
    raise SystemExit(run())

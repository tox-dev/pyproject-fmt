from __future__ import annotations

import difflib
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pyproject_fmt import Config
from pyproject_fmt.cli import PyProjectFmtNamespace, cli_args
from pyproject_fmt.formatter import format_pyproject

GREEN = "\u001b[32m"
RED = "\u001b[31m"
RESET = "\u001b[0m"


def color_diff(diff: Iterable[str]) -> Iterable[str]:
    for line in diff:
        if line.startswith("+"):
            yield f"{GREEN}{line}{RESET}"
        elif line.startswith("-"):
            yield f"{RED}{line}{RESET}"
        else:
            yield line


def _handle_one(config: Config, opts: PyProjectFmtNamespace) -> bool:
    formatted = format_pyproject(config)
    before = config.toml
    changed = before != formatted
    if opts.stdout:  # stdout just prints new format to stdout
        print(formatted, end="")
        return changed

    if before != formatted and not opts.check:
        config.pyproject_toml.write_text(formatted, encoding="utf-8")
    try:
        name = str(config.pyproject_toml.relative_to(Path.cwd()))
    except ValueError:
        name = str(config.pyproject_toml)
    diff: Iterable[str] = []
    if changed:
        diff = difflib.unified_diff(before.splitlines(), formatted.splitlines(), fromfile=name, tofile=name)

    if diff:
        diff = color_diff(diff)
        print("\n".join(diff))  # print diff on change
    else:
        print(f"no change for {name}")
    return changed


def run(args: Sequence[str] | None = None) -> int:
    opts = cli_args(sys.argv[1:] if args is None else args)
    results = [_handle_one(config, opts) for config in opts.configs]
    return 1 if any(results) else 0  # exit with non success on change


if __name__ == "__main__":
    sys.exit(run())

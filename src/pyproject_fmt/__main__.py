from __future__ import annotations

import difflib
import sys
from pathlib import Path
from typing import Iterable, Sequence

from pyproject_fmt.cli import cli_args
from pyproject_fmt.formatter import format_pyproject

GREEN = "\u001b[32m"
RED = "\u001b[31m"
RESET = "\u001b[0m"


def color_diff(diff: Iterable[str]) -> Iterable[str]:
    for line in diff:
        if line.startswith("+"):
            yield GREEN + line + RESET
        elif line.startswith("-"):
            yield RED + line + RESET
        else:
            yield line


def run(args: Sequence[str] | None = None) -> int:
    opts = cli_args(sys.argv[1:] if args is None else args)
    any_modified = False
    for config in opts.as_configs:
        formatted = format_pyproject(config)
        before = config.toml
        changed = before != formatted
        any_modified = any_modified or changed
        if opts.stdout:  # stdout just prints new format to stdout
            print(formatted, end="")
        else:
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
    # exit with non success on change
    return 1 if any_modified else 0


if __name__ == "__main__":
    sys.exit(run())

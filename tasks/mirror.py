# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "gitpython>=3.1.43",
#   "httpx>=0.27.2",
#   "packaging>=24.1",
# ]
# ///
"""Mirror missing tags."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from subprocess import check_call, check_output

import httpx
from packaging.version import Version

ROOT = Path(__file__).parents[1]


def run() -> None:
    existing_tags = set(check_output(["git", "tag"], text=True).splitlines())
    response = httpx.get("https://pypi.org/pypi/pyproject-fmt/json")
    response.raise_for_status()
    released_tags = set(response.json()["releases"].keys())

    missing_tags = sorted(Version(i) for i in released_tags - existing_tags)

    if missing_tags and os.environ.get("GITHUB_ACTIONS"):
        check_call(["git", "config", "--global", "user.email", "mirror@tox.wiki"])
        check_call(["git", "config", "--global", "user.name", "Mirroring Mike"])
    toml = ROOT / "pyproject.toml"

    for tag in missing_tags:
        print(f"Mirror {tag}")
        text = toml.read_text(encoding="utf-8")
        text = re.sub(r'version = ".*?"', f'version = "{tag}"', text)
        text = re.sub(r'"pyproject-fmt==.*"', f"pyproject-fmt=={tag}", text)
        toml.write_text(text, encoding="utf-8")
        check_call(["git", "add", "pyproject.toml"])
        check_call(["git", "commit", "-m", f"Mirror {tag}"])
        check_call(["git", "tag", str(tag)])

    if missing_tags and sys.argv[1] == "true":
        check_call(["git", "push", "--tags"])
        check_call(["git", "push"])


if __name__ == "__main__":
    run()

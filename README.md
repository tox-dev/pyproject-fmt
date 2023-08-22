# pyproject-fmt

[![PyPI](https://img.shields.io/pypi/v/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![Downloads](https://static.pepy.tech/badge/pyproject-fmt/month)](https://pepy.tech/project/pyproject-fmt)
[![PyPI - License](https://img.shields.io/pypi/l/pyproject-fmt?style=flat-square)](https://opensource.org/licenses/MIT)
[![check](https://github.com/tox-dev/pyproject-fmt/actions/workflows/check.yml/badge.svg)](https://github.com/tox-dev/pyproject-fmt/actions/workflows/check.yml)

Apply a consistent format to `pyproject.toml` files.
[Read the full documentation here](https://pyproject-fmt.readthedocs.io/en/latest/).

## add to pre-commit

```yaml
- repo: https://github.com/tox-dev/pyproject-fmt
  rev: "1.0.0"
  hooks:
    - id: pyproject-fmt
```

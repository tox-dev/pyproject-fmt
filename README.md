# pyproject-fmt

[![PyPI](https://img.shields.io/pypi/v/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyproject-fmt?style=flat-square)](https://pypistats.org/packages/pyproject-fmt)
[![PyPI - License](https://img.shields.io/pypi/l/pyproject-fmt?style=flat-square)](https://opensource.org/licenses/MIT)
![check](https://github.com/gaborbernat/pyproject-fmt/workflows/check/badge.svg?branch=main)

apply a consistent format to `pyproject.toml` files

## installation

`pip install pyproject-fmt`

## as a pre-commit hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions

Sample `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/gaborbernat/pyproject-fmt
  rev: "0.1.0"
  hooks:
    - id: pyproject-fmt
```

## cli

Consult the help for the latest usage:

```console
$ pyproject-fmt --help
```

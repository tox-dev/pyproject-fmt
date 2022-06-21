# pyproject-fmt

[![PyPI](https://img.shields.io/pypi/v/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyproject-fmt?style=flat-square)](https://pypi.org/project/pyproject-fmt)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyproject-fmt?style=flat-square)](https://pypistats.org/packages/pyproject-fmt)
[![PyPI - License](https://img.shields.io/pypi/l/pyproject-fmt?style=flat-square)](https://opensource.org/licenses/MIT)
[![check](https://github.com/tox-dev/pyproject-fmt/actions/workflows/check.yml/badge.svg)](https://github.com/tox-dev/pyproject-fmt/actions/workflows/check.yml)

Apply a consistent format to `pyproject.toml` files.
[Read the full documentation here](https://pyproject-fmt.readthedocs.io/en/latest/).

## To users of `setuptools`

This tool uses `hatchling` as a `PEP 517` build backend. Thanks to `PEP 621` the metatata is mostly unified, and in order to use `setuptools` instead you only have to apply [a small patch](./use_setuptools.patch).

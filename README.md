# pyproject-fmt mirror

[![Main](https://github.com/tox-dev/pyproject-fmt/actions/workflows/main.yaml/badge.svg)](https://github.com/tox-dev/pyproject-fmt/actions/workflows/main.yaml)

Mirror of [`pyproject-fmt`](https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt) for
[pre-commit](https://github.com/pre-commit/pre-commit).

### Using `pyproject-fmt` with pre-commit

Add it to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/pre-commit/pyproject-fmt
  rev: "" # Use the sha / tag you want to point at
  hooks:
    - id: pyproject-fmt
```

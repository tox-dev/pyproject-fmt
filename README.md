# pyproject-fmt mirror

[![Mirror](https://github.com/tox-dev/pyproject-fmt/actions/workflows/main.yaml/badge.svg)](https://github.com/tox-dev/pyproject-fmt/actions/workflows/main.yaml)

Mirror of [`pyproject-fmt`](https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt) for
[pre-commit](https://github.com/pre-commit/pre-commit).

### Using `pyproject-fmt` with pre-commit

Add it to your `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/tox-dev/pyproject-fmt
  rev: "v2.15.3"
  hooks:
    - id: pyproject-fmt
```

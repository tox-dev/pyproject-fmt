# pyproject-fmt mirror

[![Mirror](https://github.com/tox-dev/pyproject-fmt/actions/workflows/main.yaml/badge.svg)](https://github.com/tox-dev/pyproject-fmt/actions/workflows/main.yaml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/tox-dev/pyproject-fmt/badge)](https://scorecard.dev/viewer/?uri=github.com/tox-dev/pyproject-fmt)
[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/16258/badge)](https://www.bestpractices.dev/projects/16258)

Mirror of [`pyproject-fmt`](https://github.com/tox-dev/toml-fmt/tree/main/pyproject-fmt) for
[pre-commit](https://github.com/pre-commit/pre-commit).

### Using `pyproject-fmt` with pre-commit

Add it to your `.pre-commit-config.yaml`:

```yaml
  - repo: https://github.com/tox-dev/pyproject-fmt
    rev: v2.30.6
    hooks:
      - id: pyproject-fmt
```

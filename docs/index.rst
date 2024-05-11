pyproject-fmt
=============

Apply a consistent format to your ``pyproject.toml`` file with comment support.
See `changelog here <https://github.com/tox-dev/pyproject-fmt/releases>`_.

Use
---

As a CLI tool
~~~~~~~~~~~~~

Use `pipx <https://pypa.github.io/pipx/installation/>`_ to install the project:

.. code-block:: bash

   pipx install pyproject-fmt


As a ``pre-commit`` hook
~~~~~~~~~~~~~~~~~~~~~~~~

See :gh:`pre-commit/pre-commit` for instructions, sample ``.pre-commit-config.yaml``:

.. code-block:: yaml

    - repo: https://github.com/tox-dev/pyproject-fmt
      rev: "1.0.0"
      hooks:
        - id: pyproject-fmt


Calculating max supported Python version
----------------------------------------

This tool will automatically generate the ``Programming Language :: Python :: 3.X`` classifiers for you. To do so it
needs to know what is the range of Python interpreter versions you support. The lower bound can be deduced by looking
at the ``requires-python`` key in the ``pyproject.toml`` configuration file. For the upper bound by default will
assume the latest stable release but can be changed via CLI flag or config:

.. code-block:: yaml

    - repo: https://github.com/tox-dev/pyproject-fmt
      rev: "2.0.0"
      hooks:
        - id: pyproject-fmt


Command line interface
----------------------
.. sphinx_argparse_cli::
  :module: pyproject_fmt.cli
  :func: _build_cli
  :prog: pyproject-fmt
  :title:

Configuration file
------------------

The ``tool.pyproject-fmt`` table is used when present in any of the ``pyproject.toml`` files

.. code-block:: toml

    # pyproject.toml
    [tool.pyproject-fmt]
    column_width = 120
    indent = 4
    keep_full_version = false
    min_supported_python = "3.7"
    max_supported_python = "3.10"

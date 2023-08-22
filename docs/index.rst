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

Command line interface
----------------------
.. sphinx_argparse_cli::
  :module: pyproject_fmt.cli
  :func: _build_cli
  :prog: pyproject-fmt
  :title:

API
---

.. automodule:: pyproject_fmt
   :members:

.. toctree::
   :hidden:

   self

changelog
=========

v0.3.5 (2022-08-12)
-------------------
* Support ``tomlkit>=0.11`` and CPython 3.11.

v0.3.4 (2022-06-26)
-------------------
* Fix project links

v0.3.3 (2022-03-23)
-------------------
* Fix help message referring to tox.ini files

v0.3.2 (2022-03-01)
-------------------
* Fix invalid newline inside inline-table - by :user:`abravalheri`.

v0.3.1 (2022-02-27)
-------------------
* Better handling of PEP-508 dependencies by using the ``packaging`` module instead of the our own parsing logic - by
  :user:`abravalheri`.

v0.3.0 (2022-02-27)
-------------------
* Handle ``project`` section in first iteration - by :user:`gaborbernat`.
* Add documentation build to the project - by :user:`gaborbernat`.
* Add a programmatic API as :meth:`format_pyproject <pyproject_fmt.format_pyproject>` - by :user:`gaborbernat`.

v0.2.0 (2022-02-21)
-------------------
* Handle ``build-system`` section - by :user:`gaborbernat`.

v0.1.0 (2022-02-21)
-------------------
* Create base and reserve PyPI name - by :user:`gaborbernat`.

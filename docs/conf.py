from __future__ import annotations

from datetime import date, datetime

from pyproject_fmt import __version__

company, name = "tox-dev", "pyproject-fmt"
release, version = __version__, ".".join(__version__.split(".")[:2])
copyright = f"2022-{date.today().year}, {company}"
master_doc, source_suffix = "index", ".rst"

html_theme = "furo"
html_title, html_last_updated_fmt = name, datetime.now().isoformat()
pygments_style, pygments_dark_style = "sphinx", "monokai"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_argparse_cli",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

exclude_patterns = ["_build", "changelog/*", "_draft.rst"]
autoclass_content, autodoc_member_order, autodoc_typehints = "class", "bysource", "none"
autodoc_default_options = {"member-order": "bysource", "undoc-members": True, "show-inheritance": True}

extlinks = {
    "issue": (f"https://github.com/{company}/{name}/issues/%s", "#"),
    "user": ("https://github.com/%s", "@"),
    "gh": ("https://github.com/%s", ""),
}
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}
nitpicky = True
nitpick_ignore = []

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

mydir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
sys.path.insert(0, mydir)

# -- Project information -----------------------------------------------------

project = "pyoload"
copyright = "2024, ken-morel"
author = "ken-morel"

master_doc = "index"

# -- General configuration ---------------------------------------------------
autosummary_generate = True

exclude_patterns = ["build", "_build", "Thumbs.db", ".DS_Store", "_templates"]

html_static_path = ["_static"]

autoclass_content = "both"

sys.setrecursionlimit(500)
project = "pyoload"
copyright = "2024, ken-morel"
author = "ken-morel"

release = "2.0.2"
version = "2.0.2"

# -- General configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    "notfound.extension",
]

notfound_context = {
    'title': 'Page not found',
    'body': "<h1>Page not found</h1>\n\nUnfortunately we couldn't find the content you were looking for.",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "github": ("https://github.com/", None),
}
intersphinx_disabled_domains = ["std"]

templates_path = ["_templates"]

# -- Options for HTML output

html_theme = "sphinxawesome_theme"

# -- Options for EPUB output
epub_show_urls = "footnote"

rst_prolog = """\
.. role:: py(code)
  :language: python

"""

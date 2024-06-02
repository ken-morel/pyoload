# Configuration file for the Sphinx documentation builder.

# -- Project information
import sys
sys.setrecursionlimit(500)
project = 'pyoload'
copyright = '2024, ken-morel'
author = 'ken-morel'

release = '1.1.3'
version = '1.1.3'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'github': ('https://github.com/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = "sphinxawesome_theme"

# -- Options for EPUB output
epub_show_urls = 'footnote'

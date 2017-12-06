# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath('..'))
import pysnow
import sphinx_rtd_theme

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

master_doc = "index"

project = "pysnow"

version = release = pysnow.__version__

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
]

primary_domain = "py"
default_role = "py:obj"

autodoc_member_order = "bysource"
autoclass_content = "both"

autodoc_docstring_signature = False
coverage_skip_undoc_in_source = True

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'




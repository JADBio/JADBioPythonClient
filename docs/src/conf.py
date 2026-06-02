# Configuration file for the Sphinx documentation builder.

import os
import sys

# Adding project root to sys.path so autodoc imports this checkout.
sys.path.insert(0, os.path.abspath('../..'))

from jadbio import __version__

# Project information
project = 'JADBio API Python Client'
author = 'JADBio'
copyright = '2023, JADBio'
release = __version__

# Build configuration
autodoc_member_order = 'bysource'
extensions = ['sphinx.ext.viewcode', 'sphinx.ext.autodoc']
html_theme = 'classic'

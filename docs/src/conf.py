# Configuration file for the Sphinx documentation builder.

import os
import sys

from jadbio import __version__

# Adding jadbio module to sys.path
sys.path.insert(0, os.path.abspath('../../jadbio/'))

# Project information
project = 'JADBio API Python Client'
author = 'JADBio'
copyright = '2022, JADBio'
release = __version__

# Build configuration
autodoc_member_order = 'bysource'
extensions = ['sphinx.ext.viewcode', 'sphinx.ext.autodoc']
html_theme = 'classic'

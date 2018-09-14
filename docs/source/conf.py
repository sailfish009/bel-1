#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# bel documentation build configuration file, created by
# sphinx-quickstart on Mon Aug  7 15:03:45 2017.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#

import os
import sys
import sphinx_rtd_theme

# To get ReadTheDocs working - autodoc missing modules error
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
# NOTE: Must load sphinx.ext.napoleon before sphinx_autodoc_typehints.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_click.ext',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.extlinks',
    'releases',
]

extlinks = {
    'issuenum': ('https://github.com/belbio/bel/issues/%s', 'issue '),
    'project': ('https://github.com/belbio/bel/blob/master/%s', 'project file '),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'BEL Python Package'
copyright = '2017, BELBio'
author = 'William Hayes, David Chen'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.12.6'
# The full version, including alpha/beta/rc tags.
release = '0.12.6'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False


# -- Options for HTML output ----------------------------------------------

# html_theme = 'alabaster'
# html_theme_options = {
#     'description': 'A Python library that allows biologists and developers to parse, test, and validate BEL.',
#     'github_user': 'belbio',
#     'github_repo': 'bel',
#     'github_button': True,
#     'fixed_sidebar': True,
# }

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {
    'collapse_navigation': False,
    'display_version': True,
    'navigation_depth': 3,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': "both",
    # 'style_external_links': True,  # Theme error  unsupported theme option
}
html_logo = '_static/images/logo-w200.png'
html_favicon = '_static/images/favicon.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'donate.html',
    ]
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'bel_doc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'bel.tex', 'bel Documentation',
     'William Hayes, David Chen', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'bel', 'bel Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'bel', 'bel Documentation',
     author, 'bel', 'BEL tools and services.',
     'Miscellaneous'),
]




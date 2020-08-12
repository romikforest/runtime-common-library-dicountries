# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import importlib
import os
import sys

from configparser import ConfigParser

from recommonmark.transform import AutoStructify

sys.path.insert(0, os.path.abspath('../..'))
sys.setrecursionlimit(1500)

config = ConfigParser()
config.read('../../setup.cfg')
if 'docs' in config:
    config = config['docs']
else:
    config = {}


# -- Project information -----------------------------------------------------

setup_module_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
setup_module_path = os.path.join(setup_module_path, 'setup.py')
spec = importlib.util.spec_from_file_location('setup', setup_module_path)
setup_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup_module)
metadata = setup_module.metadata

project = metadata.name
copyright = metadata.lib_copyright
author = metadata.author
description = metadata.description

# The short X.Y version
version = metadata.version

# The full version, including alpha/beta/rc tags
release = metadata.version


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
    'rinoh.frontend.sphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'recommonmark',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autosummary',
    'sphinx_autodoc_typehints',
    'sphinx_markdown_tables',
    'sphinx_rtd_theme',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    # 'autoapi.extension',
    'sphinx.ext.inheritance_diagram',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = ['.rst', '.md']
source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown',
    '.md': 'markdown',
}


# The master toctree document.
master_doc = 'index'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path .
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'default'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_logo = '_static/images/logo.svg'
html_favicon = '_static/images/favicon.ico'
html_show_sphinx = False

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They're copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# html_css_files = [
#     'css/custom.css',
# ]
html_style = 'css/ditheme.css'

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# The default sidebars (for documents that don't match any pattern) are
# defined by theme itself.  Builtin themes are using these templates by
# default: ``['localtoc.html', 'relations.html', 'sourcelink.html',
# 'searchbox.html']``.
#
# html_sidebars = {}


# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = project


# -- Options for LaTeX output ------------------------------------------------
latex_engine = 'xelatex'

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',
    # The font size ('10pt', '11pt' or '12pt').
    'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    'preamble': r'\usepackage{unicode-math}',
    # Latex figure (float) alignment
    'figure_align': 'htbp',
}

latex_logo = '_static/images/logo.png'
latex_show_urls = 'inline'
latex_domain_indices = True

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, f'{project}.tex', f'{project} Documentation', f'{copyright}\n{author}', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, project, f'{project} Documentation', [f'{copyright}\n{author}'], 1)]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        master_doc,
        project,
        f'{project} Documentation',
        f'{copyright}\n{author}',
        project,
        description,
        'Miscellaneous',
    ),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']



# -- Extension configuration -------------------------------------------------

# -- Options for intersphinx extension ---------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'https://docs.python.org/': None,
    'https://mypy.readthedocs.io/en/latest/': None,
    'https://whoosh.readthedocs.io/en/latest/': None,
    'https://pytest.readthedocs.io/en/latest/': None,
    'http://pytz.sourceforge.net/': None,
}

# app setup hook
# def setup(app):
#     app.add_config_value('recommonmark_config', {
#             'url_resolver': lambda url: github_doc_root + url,
#             'auto_toc_tree_section': 'Contents',
#             }, True)
#     app.add_transform(AutoStructify)


def setup(app):
    app.add_config_value(
        'recommonmark_config',
        {
            #'url_resolver': lambda url: github_doc_root + url,
            'auto_toc_tree_section': 'Contents',
            'auto_toc_maxdepth': 6,
            'enable_auto_toc_tree': True,
            'enable_math': False,
            'enable_inline_math': False,
            'enable_eval_rst': True,
            # 'autosectionlabel_prefix_document': True,
        },
        True,
    )
    app.add_transform(AutoStructify)

show_authors = True

# autodoc:
# autodoc_mock_imports = []
# autodoc_default_options = {
#     'members': True,
#     'member-order': 'bysource',
#     'private-members': True,
#     'special-members': True,
#     'undoc-members': True,
#     # 'inherited-members': True,
#     'show-inheritance': True,
#     # 'imported-members': True,
#     'ignore-module-all': True,
#     'exclude-members': '__init__',
# }

# autosectionlabel:
autosectionlabel_prefix_document = True

# autosummary:
autosummary_generate = True
# autosummary_imported_members = True

# napoleon:
# napoleon_google_docstring = True
# napoleon_numpy_docstring = True
# napoleon_include_init_with_doc = False
# napoleon_include_private_with_doc = False
# napoleon_include_special_with_doc = True
# napoleon_use_admonition_for_examples = False
# napoleon_use_admonition_for_notes = False
# napoleon_use_admonition_for_references = False
# napoleon_use_ivar = False
# napoleon_use_param = True
# napoleon_use_rtype = True
# napoleon_type_aliases = None

# sphinx-autodoc-typehints:
set_type_checking_flag = True
typehints_fully_qualified = True
always_document_param_types = True
typehints_document_rtype = True

# sphinx.ext.todo
todo_include_todos=True

# intersphinx
# extra_intersphinx_mapping={
#     'mypy': ('https://mypy.readthedocs.io/en/latest/', None),
#     'pytest': ('https://pytest.readthedocs.io/en/latest/', None),
#     'python': ('https://docs.python.org/3', None),
#     'whoosh': ('https://whoosh.readthedocs.io/en/latest/', None),
# }

# extlinks
# extlinks = {'issue': ('https://github.com/sphinx-doc/sphinx/issues/%s',
#                       'issue ')}

# autoapi
#--------------------------
# autoapi is good to automatically document python, js, net, go code but...
# no links for terms, no typehints, sphinx_autodoc_typehints won't work with it.
# So I switch to use autosummary
# To use autoapi the settings bellow and in index.rst:
#
# .. toctree::
#     :maxdepth: 3
#     :caption: References
#     :glob:
#
#     autoapi/*

# autoapi_dirs = config.get('autoapi_dirs')
# if autoapi_dirs:
#     autoapi_dirs = set(autoapi_dirs.split(','))
# else:
#     autoapi_dirs = set()
# autoapi_dirs = [f'../../{x}' for x in autoapi_dirs]
# autoapi_type = 'python'
# autoapi_template_dir = '_templates/_autoapi'


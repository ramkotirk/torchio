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
import os
import sys
from typing import List
sys.path.insert(0, os.path.abspath('../..'))
sys.path.append(os.path.abspath('sphinxext'))

# -- Project information -----------------------------------------------------

project = 'TorchIO'
copyright = '2020, Fernando Pérez-García'  # noqa: A001
author = 'Fernando Pérez-García'

# version is the short X.Y version
# release is the full version, including alpha/beta/rc tags
version = release = '0.18.61'


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx_copybutton',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'matplotlib.sphinxext.plot_directive',
    'sphinx_gallery.gen_gallery',
    'notfound.extension',
]

# Add mappings
# https://kevin.burke.dev/kevin/sphinx-interlinks/
# https://github.com/pytorch/fairseq/blob/adb5b9c71f7ef4fe2f258e0da102d819ab9920ef/docs/conf.py#L131
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'torch': ('https://pytorch.org/docs/master/', None),
    'torchvision': ('https://pytorch.org/docs/master/', None),
    'nibabel': ('https://nipy.org/nibabel/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
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

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns: List[str] = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = None

# sphinx-notfound-page
# https://github.com/readthedocs/sphinx-notfound-page
notfound_context = {
    'title': 'Page not found',
    'body': (
        '<h1>Page not found</h1>'
        "<p>Sorry, we couldn't find that page.</p>"
        '<p>Try using the search box or go to the'
        ' <a href="http://torchio.rtfd.io/">homepage</a>.</p>'
    ),
}

# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-nitpicky
# This generates a lot of warnings because of the broken internal links, which
# makes the docs build fail because of the "fail_on_warning: true" option in
# the .readthedocs.yml config file
# nitpicky = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

html_favicon = 'favicon_io/favicon.ico'
html_logo = 'favicon_io/torchio_logo_2048x2048.png'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
url = 'https://doi.org/10.1016/j.cmpb.2021.106236'
html_href = f'<a href="{url}">paper</a>'
message = f'The new peer-reviewed TorchIO {html_href} is out!'
html_theme_options = {
    'announcement': message,
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

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
htmlhelp_basename = 'TorchIOdoc'


# -- Options for LaTeX output ------------------------------------------------

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
    (master_doc, 'TorchIO.tex', 'TorchIO Documentation',
     'Fernando Pérez-García', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'torchio', 'TorchIO Documentation',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'TorchIO', 'TorchIO Documentation',
     author, 'TorchIO', 'One line description of project.',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# CopyButton configuration
copybutton_prompt_text = r'>>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: '  # noqa: E501,FS003
copybutton_prompt_is_regexp = True

# def setup(app):
#     app.add_js_file('copybutton.js')


# -- Extension configuration -------------------------------------------------

sphinx_gallery_conf = {
    'examples_dirs': '../examples',   # example scripts
    'gallery_dirs': 'auto_examples',  # where to save gallery generated output
    'matplotlib_animations': True,
    'binder': {
        # Required keys
        'org': 'fepegar',
        'repo': 'torchio',
        'branch': 'main',
        'binderhub_url': 'https://mybinder.org',
        'dependencies': '../requirements.txt',
        # Optional keys
        'use_jupyter_lab': False,
    }
}

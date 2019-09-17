# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

# Add the project root and sandbox root to the path
import sys
import os
fiesta_folder = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '../..'))
sandbox_folder = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '../../sandbox'))
sys.path.append(fiesta_folder)
sys.path.append(sandbox_folder)

# Specify settings module (which will be picked up from the sandbox)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings_sphinx')

import django
django.setup()




# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinxcontrib.napoleon',
    'sphinx_issues',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# -- Project information -----------------------------------------------------
project = 'django-fiesta'
copyright = '2019, Antonis Loumiotis'
author = 'Antonis Loumiotis'

# The full version, including alpha/beta/rc tags
from fiesta import __version__
release = __version__.__version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_draft']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Github repo for sphinx-issues
issues_github_path = 'django-fiesta/django-fiesta'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'fiesta-oscar.tex', 'fiesta-oscar Documentation',
   'Antonis Loumiotis', 'manual'),
]

# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'fiesta-oscar', 'django-fiesta Documentation',
     ['Antonis Loumiotis'], 1)
]

# Autodoc settings
autoclass_content = 'class'

import inspect
from django.utils.html import strip_tags
from django.utils.encoding import force_text


def process_docstring(app, what, name, obj, options, lines):
    # This causes import errors if left outside the function
    from django.db import models

    # Only look at objects that inherit from Django's base model class
    if inspect.isclass(obj) and issubclass(obj, models.Model):

        # Ignore abstract models
        if not hasattr(obj._meta, '_fields'):
            return lines

        # Grab the field list from the meta class
        fields = obj._meta._fields()

        for field in fields:
            # Decode and strip any html out of the field's help text
            help_text = strip_tags(force_text(field.help_text))

            # Decode and capitalize the verbose name, for use if there isn't
            # any help text
            verbose_name = force_text(field.verbose_name).capitalize()

            if help_text:
                # Add the model field to the end of the docstring as a param
                # using the help text as the description
                lines.append(':param %s: %s' % (field.attname, help_text))
            else:
                # Add the model field to the end of the docstring as a param
                # using the verbose name as the description
                lines.append(':param %s: %s' % (field.attname, verbose_name))

            # Add the field's type to the docstring
            lines.append(':type %s: %s' % (field.attname, type(field).__name__))

    # Return the extended docstring
    return lines

def setup(app):
    # Register the docstring processor with sphinx
    app.connect('autodoc-process-docstring', process_docstring)

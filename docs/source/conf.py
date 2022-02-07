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
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import pathlib
import shutil
import sys

import sphinx.ext.apidoc


SCRIPT_DIR = pathlib.Path(__file__).parent
MODULE_DIR = pathlib.Path(__file__).parent.parent / "dug_seis_acquisition"

sys.path.insert(0, str(SCRIPT_DIR.parent))


# -- Project information -----------------------------------------------------

project = 'DUGseis-acquisition'
copyright = '2022, T. Haag, L. Villiger'
author = 'T. Haag, L. Villiger'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser',
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_book_theme"
html_logo = "_static/dug_seis_acquisition_logo.svg"
html_theme_options = {
    "github_url": "https://github.com/swiss-seismological-service/DUGseis-acquisition",
    "repository_url": "https://github.com/swiss-seismological-service/DUGseis-acquisition",
    "use_edit_page_button": True,
    "repository_branch": "main",
    "path_to_docs": "docs",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# intersphinx_mapping = {
#     "python": ("https://docs.python.org/3.9", None),
# }
#
# # Automatically build sphinx ext apidoc.
# # Adapted from https://github.com/readthedocs/readthedocs.org/issues/1139
# def run_apidoc(*args, **kwargs):
#     output_path = SCRIPT_DIR / ".generated"
#     # Make sure to have a clean build.
#     if output_path.exists():
#         shutil.rmtree(output_path)
#     print(f"Autogenerating API doc in '{output_path}'")
#     sphinx.ext.apidoc.main(
#         [
#             "-e",
#             "--force",
#             "-o",
#             str(output_path),
#             str(MODULE_DIR),
#             # All remaining items are folders to be ignored.
#             str(MODULE_DIR / "graphical_interface"),
#         ]
#     )
#
#
# def setup(app):
#     app.connect("builder-inited", run_apidoc)
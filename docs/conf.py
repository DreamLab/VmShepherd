# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys

sys.path.insert(0, os.path.abspath('../src'))


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.graphviz',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = 'VmShepherd'
year = '2019'
author = 'Dreamlab'
copyright = '{0}, {1}'.format(year, author)
version = release = '1.5.2'

pygments_style = 'sphinx'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/Dreamlab/vmshepherd/issues/%s', '#'),
    'pr': ('https://github.com/Dreamlab/vmshepherd/pull/%s', 'PR #'),
}
# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only set the theme if we're building docs locally
    html_theme = 'sphinx_rtd_theme'

html_use_smartypants = True
html_last_updated_fmt = '%b %d, %Y'
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
}
html_short_title = '%s-%s' % (project, version)

html_context = {
    "display_github": True,
    "github_user": "DreamLab",
    "github_repo": "VmShepherd",
    "github_version": "master",
    "conf_py_path": "/docs/",
}

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False

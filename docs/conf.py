# -*- coding: utf-8 -*-

import os
import sys
import shlex

import alabaster


sys.path.insert(0, os.path.abspath('..'))


extensions = [
    'alabaster',
    'sphinx.ext.pngmath',
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'seismograph'
copyright = u'2015, M.Trifonov'
author = u'M.Trifonov'

version = '0.5.x'
release = '0.5.x'

language = None
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False

html_theme = 'alabaster'
html_theme_path = [
    alabaster.get_path(),
]
html_theme_options = {
    # 'logo': 'logo.png',
    'logo_name': 'seismograph',
    'description': ' ',
    'github_button': False,
    'github_banner': True,
    'show_powered_by': False,
    'github_user': 'trifonovmixail',
    'github_repo': 'seismograph',
}
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',
        'searchbox.html',
        'donate.html',
    ],
}

html_static_path = ['_static']
htmlhelp_basename = 'seismographdoc'

latex_elements = {}
latex_documents = [
  (master_doc, 'seismograph.tex', u'seismograph Documentation',
   u'M.Trifonov', 'manual'),
]

man_pages = [
    (master_doc, 'seismograph', u'seismograph Documentation',
     [author], 1)
]

texinfo_documents = [
  (master_doc, 'seismograph', u'seismograph Documentation',
   author, 'seismograph', 'One line description of project.',
   'Miscellaneous'),
]

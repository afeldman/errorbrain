# Configuration file for Sphinx documentation

project = 'ErrorBrain'
copyright = '2024, ErrorBrain Contributors'
author = 'ErrorBrain Contributors'
release = '0.1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.imgmath',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
    'sphinxcontrib.spelling',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = None
html_favicon = None

html_theme_options = {
    'canonical_url': 'https://errorbrain.io/docs/',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, 'errorbrain.tex', 'ErrorBrain Documentation',
     'ErrorBrain Contributors', 'manual'),
]

man_pages = [
    (master_doc, 'errorbrain', 'ErrorBrain Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'errorbrain', 'ErrorBrain Documentation',
     author, 'errorbrain', 'AI-powered debugging memory',
     'Miscellaneous'),
]

intersphinx_mapping = {'https://docs.python.org/3': None}

todo_include_todos = True

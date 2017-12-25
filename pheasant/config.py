import codecs
import os

import pheasant

config = {}

template = os.path.join(os.path.dirname(pheasant.__file__),
                        'templates/markdown.jinja2')
config['notebook'] = {'format_version': 4, 'template': template,
                      'language': 'python', 'timeout': 600,
                      'kernel': 'python3'}

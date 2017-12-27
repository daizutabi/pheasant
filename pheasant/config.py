import os

import pheasant

config = {}

template = os.path.join(os.path.dirname(pheasant.__file__),
                        'templates/markdown.jinja2')
config['jupyter'] = {'format_version': 4, 'template': template,
                     'timeout': 600,
                     'kernel_name': {'python': 'python3'}}

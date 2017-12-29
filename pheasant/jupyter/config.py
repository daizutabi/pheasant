import os

template_file = os.path.join(os.path.dirname(__file__),
                             'templates/markdown.jinja2')
config = {'format_version': 4, 'template_file': template_file, 'timeout': 600,
          'kernel_name': {'python': 'python3'}, 'output_format': 'html'}

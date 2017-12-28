import os

from pheasant import config as pheasant_config

template_file = os.path.join(os.path.dirname(__file__),
                             'templates/markdown.jinja2')
config = {'format_version': 4, 'template_file': template_file, 'timeout': 600,
          'kernel_name': {'python': 'python3'}, 'output_format': 'html'}

pheasant_config['jupyter'] = config


def set_config(update_config):
    if 'kernel_name' in update_config:
        config['kernel_name'].update(update_config['kernel_name'])
        update_config['kernel_name'] = config['kernel_name']

    config.update(update_config)

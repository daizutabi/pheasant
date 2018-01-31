import os

from jinja2 import FileSystemLoader

from .config import config
from .markdown import convert as convert_markdown
from .notebook import convert as convert_notebook
from .notebook import new_exporter


def initialize():
    default_directory = os.path.join(os.path.dirname(__file__), 'templates')
    abspath = os.path.abspath(config['template_file'])
    template_directory, template_file = os.path.split(abspath)
    loader = FileSystemLoader([template_directory, default_directory])
    # env = Environment(
    #     loader=FileSystemLoader([template_directory, default_directory]),
    #     autoescape=False
    # )
    # config['loader'] = template_file
    # config['template_file'] = template_file
    config['exporter'] = new_exporter(loader, template_file)


def convert(source):
    if not isinstance(source, str) or (os.path.exists(source) and
                                       source.endswith('.ipynb')):
        source = convert_notebook(source)
    else:
        source = convert_markdown(source)

    if config['output_format'] == 'notebook':
        source = str(source)

    return source

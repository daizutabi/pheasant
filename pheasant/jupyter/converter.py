import os

from .config import config
from .markdown import convert as convert_markdown
from .notebook import convert as convert_notebook


def convert(source):
    if not isinstance(source, str) or (os.path.exists(source) and
                                       source.endswith('.ipynb')):
        source = convert_notebook(source)
    else:
        source = convert_markdown(source)

    if config['output_format'] == 'notebook':
        source = str(source)

    return source

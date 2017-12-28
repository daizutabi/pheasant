import os

from .config import config
from .markdown import convert as convert_markdown
from .notebook import convert as convert_notebook


def convert(source):
    output_format = config['output_format']

    # FIXME: change if-else
    if not isinstance(source, str):
        # `source` must be a Notebook object.
        output = convert_notebook(source, output_format=output_format)
    elif os.path.exists(source):
        if source.endswith('.ipynb'):
            output = convert_notebook(source, output_format=output_format)
        else:
            output = convert_markdown(source, output_format=output_format)
    else:
        # it is markdown
        output = convert_markdown(source, output_format=output_format)

    return output

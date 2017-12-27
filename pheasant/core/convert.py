import os

from pheasant.core.markdown import convert as convert_markdown
from pheasant.core.notebook import convert as convert_notebook


def convert(source, output='markdown'):
    if not isinstance(source, str):
        # `source` must be a Notebook object.
        output = convert_notebook(source, output=output)
    elif os.path.exists(source):
        if source.endswith('.ipynb'):
            output = convert_notebook(source, output=output)
        else:
            output = convert_markdown(source, output=output)
    else:
        # it is markdown
        output = convert_markdown(source, output=output)

    return output

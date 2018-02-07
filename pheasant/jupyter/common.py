import re

import nbformat

from .client import run_cell
from .config import config


def preprocess_markdown(source: str):
    if source.startswith('```') or source.startswith('~~~'):
        return source

    source = evaluate_markdown(source)
    source = inspect_markdown(source)

    return source


def evaluate_markdown(source: str, kernel_name=None):
    """
    Evaluate {{expr}} in Markdown source.

    If expr starts with '#', expr is not evaluated: {{#abc}} -> {{abc}}

    """
    kernel_name = kernel_name or config['python_kernel']

    def replace(m):
        code = m.group(1)

        # {{#abc}} -> {{abc}}
        if code.startswith('#'):
            return m.group().replace(code, code[1:])

        cell = nbformat.v4.new_code_cell(code.strip())
        run_cell(cell, kernel_name)

        notebook = nbformat.v4.new_notebook(cells=[cell], metadata={})
        markdown = config['inline_exporter'].from_notebook_node(notebook)[0]
        return markdown

    return re.sub(config['inline_pattern'], replace, source)


def inspect_markdown(source, kernel_name=None):
    """
    Inspect source code.

    #Code <object name>
    """
    kernel_name = kernel_name or config['python_kernel']

    def replace(m):
        name, *options = m.group(1).split(' ')
        name, *line_range = name.split(':')

        cell = nbformat.v4.new_code_cell(f'inspect.getsourcelines({name})')
        run_cell(cell, kernel_name)

        source = ''
        for output in cell['outputs']:
            if 'data' in output and 'text/plain' in output['data']:
                lines, lineno = eval(output['data']['text/plain'])
                break

        source = ''.join(lines)
        source = m.group() + f'\n\n#begin\n``` python\n{source}```\n#end'
        return source

    return re.sub(config['code_pattern'], replace, source, flags=re.MULTILINE)

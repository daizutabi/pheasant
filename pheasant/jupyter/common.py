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

    For `{{` or `}}` iteself, use `{{{` or `}}}`.

    """
    kernel_name = kernel_name or config['python_kernel']

    def replace(m):
        code = m.group()

        # {{{xxx}}} -> {{xxx}}
        if code.startswith('{{{') and code.endswith('}}}'):
            return code[1:-1]

        cell = nbformat.v4.new_code_cell(code[2:-2].strip())
        run_cell(cell, kernel_name)

        # TODO: other formats than text/plain
        for output in cell['outputs']:
            if 'data' in output and 'text/plain' in output['data']:
                text = output['data']['text/plain']
                if text.startswith('\'') and text.endswith('\''):
                    text = text[1:-1]
                return text
        else:
            return ''

    return re.sub(r'\{{2,3}(.+?)\}{2,3}', replace, source)


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

    return re.sub(r'^#Code (.+)$', replace, source, flags=re.MULTILINE)

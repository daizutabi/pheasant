import re

import nbformat
from markdown import Markdown

from .client import run_cell
from .config import config


def preprocess_code(source: str):

    func = 'pheasant.jupyter.convert_inline'

    def replace(m):
        code = m.group(1)

        if code.startswith('#'):  # {{#abc}} -> {{abc}}
            return m.group().replace(code, code[1:])
        elif code.startswith('!'):
            code = code[1:]
            return f'{func}({code}, output="html")'
        else:
            return f'{func}({code}, output="markdown")'

    return re.sub(config['inline_pattern'], replace, source)


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

    If expr starts with '!', expr is converted into HTML after execution.
    """
    kernel_name = kernel_name or config['python_kernel']

    extensions = ['tables', 'fenced_code']
    md = Markdown(extensions=extensions + config['markdown_extensions'])

    def replace(m):
        code = m.group(1)

        # {{#abc}} -> {{abc}}
        if code.startswith('#'):
            return m.group().replace(code, code[1:])

        # Markdown -> HTML
        to_html = False
        if code.startswith('!'):
            code = code[1:]
            to_html = True

        cell = nbformat.v4.new_code_cell(code.strip())
        run_cell(cell, kernel_name)

        markdown = inline_export(cell)

        if to_html:
            markdown = md.convert(markdown)

        return markdown

    return re.sub(config['inline_pattern'], replace, source)


def inline_export(cell, escape=False):
    """Convert a cell into markdown with `inline_template`."""
    notebook = nbformat.v4.new_notebook(cells=[cell], metadata={})
    markdown = config['inline_exporter'].from_notebook_node(notebook)[0]

    if escape:
        # FIXME
        markdown = f'{markdown}'
    elif markdown.startswith("'") and markdown.endswith("'"):
        markdown = str(eval(markdown))

    return markdown


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

import re

import nbformat
from markdown import Markdown

from .config import config
from .exporter import inline_export, inspect_export, run_and_export


def preprocess_code(source: str) -> str:

    func = 'pheasant.jupyter.convert_inline'

    def replace(m):
        code = m.group(1)

        if code.startswith(config['inline_ignore_character']):
            return m.group().replace(code, code[1:])
        elif code.startswith(config['inline_html_character']):
            return f'{func}({code[1:]}, output="html")'
        else:
            return f'{func}({code}, output="markdown")'

    return re.sub(config['inline_pattern'], replace, source)


def preprocess_markdown(source: str) -> str:
    if source.startswith('```') or source.startswith('~~~'):
        return source

    source = evaluate_markdown(source)
    source = inspect_markdown(source)

    return source


def evaluate_markdown(source: str) -> str:
    """
    Evaluate {{expr}} in Markdown source.

    If expr starts with '#', expr is not evaluated: {{#abc}} -> {{abc}}

    If expr starts with '^', expr is converted into HTML after execution.

    Above settings is default values and configurable.
    """
    extensions = ['tables', 'fenced_code']
    md = Markdown(extensions=extensions + config['markdown_extensions'])

    def replace(m):
        code = m.group(1)

        if code.startswith(config['inline_ignore_character']):
            return m.group().replace(code, code[1:])

        to_html = code.startswith(config['inline_html_character'])
        if to_html:
            code = code[1:]

        cell = nbformat.v4.new_code_cell(code.strip())

        markdown = run_and_export(cell, inline_export)

        if to_html:
            return md.convert(markdown)
        else:
            return markdown

    return re.sub(config['inline_pattern'], replace, source)


def inspect_markdown(source):
    """
    Inspect source code.

    #Code <object name>
    """
    def replace(m):
        name, *options = m.group(1).split(' ')
        name, *line_range = name.split(':')

        cell = nbformat.v4.new_code_cell(f'inspect.getsourcelines({name})')
        markdown = run_and_export(cell, inspect_export)

        return m.group() + f'\n\n#begin\n``` python\n{markdown}```\n#end'

    return re.sub(config['code_pattern'], replace, source, flags=re.MULTILINE)

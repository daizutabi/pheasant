"""Evaluate {{expr}} in Markdown source and fenced code.

If expr starts with '#', expr is not evaluated: {{#abc}} -> {{abc}}

If expr starts with '^', expr is converted into HTML after execution.

Above settings is default values and configurable.
"""

import re
from typing import Match

import nbformat

from pheasant.jupyter.config import config
from pheasant.jupyter.renderer import inline_render, run_and_render


def replace(match: Match, ignore_equal: bool = False) -> str:
    convert = 'pheasant.jupyter.display'
    source = match.group(1)

    if '=' in source and not ignore_equal:
        return source

    if source.startswith(config['inline_html_character']):
        source = source[1:]
        output = 'html'
    else:
        output = 'markdown'

    if source.startswith(config['inline_display_character']):
        source = source[1:]

    if ';' in source:
        sources = source.split(';')
        source = '_pheasant_dummy'
        sources[-1] = f'{source} = {sources[-1]}'
        sources = '\n'.join(sources)
        cell = nbformat.v4.new_code_cell(sources)
        run_and_render(cell, inline_render)

    return f'{convert}({source}, output="{output}")'


def preprocess_code(source: str) -> str:
    def replace_(match):
        return replace(match, ignore_equal=True)

    return re.sub(config['inline_pattern'], replace_, source)


def preprocess_markdown(source: str) -> str:
    if source[:3] in ['```', '~~~', '<di']:  # escaped or already converted.
        return source

    def replace_and_run(match: Match) -> str:
        source = match.group(1)
        if source.startswith(config['inline_ignore_character']):
            return match.group().replace(source, source[1:])

        display = source.startswith(config['inline_display_character'])
        source = replace(match)
        cell = nbformat.v4.new_code_cell(source)
        return run_and_render(cell, inline_render, display=display)

    return re.sub(config['inline_pattern'], replace_and_run, source)

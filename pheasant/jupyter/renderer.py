import re
from typing import Callable

import nbformat
from nbformat import NotebookNode

from .cache import abort, memoize
from .client import run_cell, select_kernel_name
from .config import config


def new_code_cell(source: str, language=None, options=None) -> NotebookNode:
    """Create a new code cell for evaluation."""
    cell = nbformat.v4.new_code_cell(source)
    metadata = {}
    if language is not None:
        metadata['language'] = language
        kernel_name = select_kernel_name(language)
        metadata['kernel_name'] = kernel_name
    if options is not None:
        metadata['options'] = options
    cell.metadata['pheasant'] = metadata
    return cell


def render(cell: NotebookNode) -> str:
    """Convert a cell into markdown with `template`."""
    return config['template'].render(cell=cell)


def inline_render(cell: NotebookNode) -> str:
    """Convert a cell into markdown with `inline_template`."""
    strip_text(cell)
    markdown = config['inline_template'].render(cell=cell)

    if markdown.startswith("'") and markdown.endswith("'"):
        markdown = str(eval(markdown))

    return markdown


def pheasant_options(cell: NotebookNode) -> list:
    """Get pheasant options from cell's metadata."""
    if 'pheasant' in cell.metadata:
        return cell.metadata['pheasant']['options']
    else:
        return []


@abort
@memoize
def run_and_render(cell: NotebookNode, render: Callable[..., str],
                   kernel_name=None) -> str:
    """Run a code cell and render the source and outputs into markdown.

    These two functions are defined in this function in order to cache the
    source and outputs to avoid rerunning the cell unnecessarily.
    """
    run_cell(cell, kernel_name)
    # print(cell)

    select_display_data(cell)
    source = render(cell)
    # print(f'>>{source}<<')
    return source


display_data_priority = ['application/vnd.jupyter.widget-state+json',
                         'application/vnd.jupyter.widget-view+json',
                         'application/javascript',
                         'text/html',
                         'text/markdown',
                         'image/svg+xml',
                         'text/latex',
                         'image/png',
                         'image/jpeg',
                         'text/plain']


def select_display_data(cell: NotebookNode) -> None:
    re_compile = re.compile(r'<style scoped>.*?</style>', flags=re.DOTALL)
    for output in cell.outputs:
        for data_type in display_data_priority:
            if 'data' in output and data_type in output['data']:
                text = output['data'][data_type]
                if data_type == 'text/html':  # for Pandas DataFrame
                    text = re_compile.sub('', text)
                output['data'] = {data_type: text}
                break


def strip_text(cell: NotebookNode) -> None:
    for output in cell.outputs:
        if output['output_type'] == 'execute_result':
            if 'text/plain' in output['data']:
                text = output['data']['text/plain']
                if text.startswith("'"):
                    text = eval(text)
                output['data'] = {'text/plain': text}
                break

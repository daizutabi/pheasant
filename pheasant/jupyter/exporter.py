from typing import Callable

import nbformat
from nbconvert import MarkdownExporter
from nbformat import NotebookNode
from traitlets.config import Config

from .cache import abort, memoize
from .client import run_cell, select_kernel_name
from .config import config


def new_exporter(loader=None, template_file=None):
    c = Config({'NbConvertBase': {
        'display_data_priority': ['application/vnd.jupyter.widget-state+json',
                                  'application/vnd.jupyter.widget-view+json',
                                  'application/javascript',
                                  'text/html',
                                  'text/markdown',
                                  'image/svg+xml',
                                  'text/latex',
                                  'image/png',
                                  'image/jpeg',
                                  'text/plain']
    }})

    exporter = MarkdownExporter(config=c,
                                extra_loaders=[loader] if loader else None)
    exporter.template_file = template_file
    return exporter


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


def export(cell) -> str:
    """Convert a cell into markdown with `template`."""
    notebook = nbformat.v4.new_notebook(cells=[cell], metadata={})
    markdown = config['exporter'].from_notebook_node(notebook)[0]
    return markdown


def inline_export(cell) -> str:
    """Convert a cell into markdown with `inline_template`."""
    notebook = nbformat.v4.new_notebook(cells=[cell], metadata={})
    markdown = config['inline_exporter'].from_notebook_node(notebook)[0]

    if markdown.startswith("'") and markdown.endswith("'"):
        markdown = str(eval(markdown))

    return markdown


@abort
@memoize
def run_and_export(cell, export: Callable[..., str], kernel_name=None) -> str:
    """Run a code cell and export the source and outputs into markdown.

    These two functions are defined in this function in order to cache the
    source and outputs to avoid rerunning the cell unnecessarily.
    """
    run_cell(cell, kernel_name)
    # print('++++++++++++++++++++++++')
    # if 'outputs' in cell:
    #     for output in cell['outputs']:
    #         print('------------------------')
    #         print(output['output_type'])
    #         if 'data' in output:
    #             print(list(output['data'].keys()))
    return export(cell)

from typing import Callable

import nbformat
from nbconvert import MarkdownExporter
from traitlets.config import Config

from .cache import abort, memoize
from .client import run_cell
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
    return export(cell)

import re
from typing import Any, Callable, Dict, Optional

import nbformat
from nbformat import NotebookNode

from .cache import abort, memoize
from .client import run_cell, select_kernel_name
from .config import config


def new_code_cell(source: str,
                  language: Optional[str] = None,
                  options: Optional[list] = None) -> NotebookNode:
    """Create a new code cell for evaluation."""
    cell = nbformat.v4.new_code_cell(source)
    metadata: Dict[str, Any] = {}
    if language is not None:
        metadata['language'] = language
        kernel_name = select_kernel_name(language)
        metadata['kernel_name'] = kernel_name
    if options is not None:
        metadata['options'] = options
    cell.metadata['pheasant'] = metadata
    return cell


def render(cell: NotebookNode) -> str:
    """Convert a cell into markdown or html with `template`."""
    return config['template'].render(cell=cell)


def inline_render(cell: NotebookNode, display=False) -> str:
    """Convert a cell into markdown or html with `inline_template`."""
    strip_text(cell)
    return config['inline_template'].render(cell=cell, display=display)


def pheasant_options(cell: NotebookNode) -> list:
    """Get pheasant options from cell's metadata."""
    if 'pheasant' in cell.metadata:
        return cell.metadata['pheasant']['options']
    else:
        return []


@abort
@memoize
def run_and_render(cell: NotebookNode, render: Callable[..., str],
                   kernel_name: Optional[str] = None, **kwargs) -> str:
    """Run a code cell and render the source and outputs into markdown."""

    # These two functions are defined in this function in order to cache the
    # source and outputs to avoid rerunning the cell unnecessarily.
    run_cell(cell, kernel_name)
    select_display_data(cell)
    return render(cell=cell, **kwargs)


display_data_priority = [
    'application/vnd.jupyter.widget-state+json',
    'application/vnd.jupyter.widget-view+json', 'application/javascript',
    'text/html', 'text/markdown', 'image/svg+xml', 'text/latex', 'image/png',
    'image/jpeg', 'text/plain'
]


def select_display_data(cell: NotebookNode) -> None:
    """Select display data with the highest priority."""
    for output in cell.outputs:
        for data_type in display_data_priority:
            if 'data' in output and data_type in output['data']:
                text = output['data'][data_type]
                if data_type == 'text/html' and '"dataframe"' in text:
                    text = delete_style(text)
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


pandas_pattern = (r'(<style scoped>.*?</style>)|( border="1")|'
                  r'( style="text-align: right;")')
pandas_re_compile = re.compile(pandas_pattern, flags=re.DOTALL)


def delete_style(html: str) -> str:
    """Delete style from Pandas DataFrame html."""
    return pandas_re_compile.sub('', html)

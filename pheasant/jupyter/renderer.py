import re
from typing import Any, Callable, Dict, Optional

import nbformat
from nbformat import NotebookNode

from pheasant.jupyter.cache import abort, memoize
from pheasant.jupyter.client import run_cell, select_kernel_name
from pheasant.jupyter.config import config


def new_code_cell(source: str, language: Optional[str] = None,
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


def inline_render(cell: NotebookNode, display: bool = False) -> str:
    """Convert a cell into markdown or html with `inline_template`."""
    strip_text(cell)
    return config['inline_template'].render(cell=cell, display=display)


def pheasant_options(cell: NotebookNode) -> list:
    """Get pheasant options from the cell's metadata."""
    if 'pheasant' in cell.metadata:
        return cell.metadata['pheasant']['options']
    else:
        return []

# `run_and_render` function is 'memoize'-decorated in order to cache the
# source and outputs to avoid rerunning the same cell unnecessarily.
@abort
@memoize
def run_and_render(cell: NotebookNode, render: Callable[..., str],
                   kernel_name: Optional[str] = None,
                   callback: Optional[Callable[[NotebookNode], None]] = None,
                   select_display: bool = True, **kwargs) -> str:
    """Run a code cell and render the source and outputs into markdown.

    Parameters
    ----------
    cell : NotebookNode
        Input notebook cell.
    render : callable
        Rendering function for the output cell.
    kernel_name : str, optional
        Name of a jupyter kernel to execute the input cell.
    callback : callable, optional
        Callback function which is called after cell execution.
    select_display : bool, optional
        If True, select display data with the highest priority.
    **kwars:
        Additional parameters for the render function.

    Returun
    -------
    str
        rendered string
    """
    run_cell(cell, kernel_name)
    if select_display:
        select_display_data(cell)
    if callback:
        callback(cell)
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
            if 'text/html' in output['data']:
                return
            elif 'text/plain' in output['data']:
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

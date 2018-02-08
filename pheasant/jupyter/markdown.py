import re

import nbformat

from ..utils import escaped_splitter, read_source
from .client import run_cell, select_kernel_name
from .preprocess import preprocess_code, preprocess_markdown, inline_export
from .notebook import convert as convert_notebook
from .notebook import update_cell_metadata


def convert(source: str, **kwargs):
    """
    Convert markdown string or file into markdown with running results.

    Parameters
    ----------
    source : str
        Markdown source string or filename
    output_format : str
        Output format. If `notebook`, notebook object is returned
        after running but before converting into markdown.
        This is useful for debugging.

    Returns
    -------
    results : str
        Markdown source
    """
    source = read_source(source)
    cells = list(cell_runner(source))
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={})

    return convert_notebook(notebook, **kwargs)


def cell_runner(source: str):
    """
    Generate cell with outputs after running the code
    from markdown source string.

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    cell : Cell
        Cell with outputs.
    """
    for cell in cell_generator(source):
        if cell.cell_type != 'code':
            cell.source = preprocess_markdown(cell.source)
            yield cell
        else:
            pheasant_metadata = cell.metadata.get('pheasant', {})
            language = pheasant_metadata.get('language', 'python')
            kernel_name = select_kernel_name(language)

            if 'inline' in cell.metadata['pheasant']['options']:
                cell.source = preprocess_code(cell.source)
                cell = run_cell(cell, kernel_name)
                markdown = inline_export(cell)
                yield nbformat.v4.new_markdown_cell(markdown)
            else:
                cell = run_cell(cell, kernel_name)
                yield cell


def cell_generator(source: str):
    """
    Generate notebook cell from markdown source string.
    Generated cell has no outputs.

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    cell : Cell
        Markdown cell or code cell.
    """
    for splitted in fenced_code_splitter(source):
        if isinstance(splitted, str):
            yield nbformat.v4.new_markdown_cell(splitted)
        else:
            language, code, option = splitted
            cell = nbformat.v4.new_code_cell(code)
            update_cell_metadata(cell, language, option)
            yield cell


def fenced_code_splitter(source: str):
    """
    Generate splitted markdown and jupyter notebook cell from `source`.
    The type of generated value is str or tuple.
    If str, it is markdown.
    If tuple, it is (language, code, option). See below:

    source:
        <markdown>

        ```<language> <option>
        ## <option>
        <code>
        ```
        ...

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    cell_string : str or tuple
    """
    pattern_escape = r'^~~~$.*?^~~~$'
    pattern_code = r'^```(\S+)([^\n.]*)\n(.*?)\n^```$'
    re_option = re.DOTALL | re.MULTILINE

    for splitted in escaped_splitter(pattern_code, pattern_escape, source,
                                     option=re_option):
        if isinstance(splitted, str):
            markdown = splitted.strip()
            if markdown:
                yield markdown
        else:
            language = splitted.group(1)
            if select_kernel_name(language) is None:
                yield splitted.group()
            else:
                code = splitted.group(3).strip()
                option = splitted.group(2).strip()
                if code.startswith('## '):
                    option += code.split('\n')[0][3:]
                yield language, code, option

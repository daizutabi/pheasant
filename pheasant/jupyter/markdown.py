import os
import re

import nbformat

from .client import run_cell, select_kernel_name
from .notebook import convert as convert_notebook
from .notebook import update_cell_metadata


def convert(source: str, output_format='markdown'):
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
    if os.path.exists(source):
        with open(source) as f:
            source = f.read()

    cells = list(cell_runner(source))
    notebook = nbformat.v4.new_notebook(cells=cells, metadata={})

    if output_format == 'notebook':
        return notebook
    else:
        markdown = convert_notebook(notebook)
        return markdown


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
            yield cell
            continue

        pheasant_metadata = cell.metadata.get('pheasant', {})
        language = pheasant_metadata.get('language', 'python')
        kernel_name = select_kernel_name(language)
        cell = run_cell(kernel_name, cell)
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
    for cell in fenced_code_splitter(source):
        if isinstance(cell, str):
            yield nbformat.v4.new_markdown_cell(cell)
        else:
            language, code, option = cell
            cell = nbformat.v4.new_code_cell(code)
            yield update_cell_metadata(cell, language, option)


def fenced_code_splitter(source: str):
    """
    Generate splitted markdown and jupyter notebook cell from `source`.
    The type of generated value is str or tuple.
    If str, it is markdown.
    If tuple, it is (language, code, option). See below:

    source:
        <markdown>

        ```<language> <option>
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
    pattern = r'^```(\S+)([^\n.]*)\n(.*?)\n^```$'
    re_compile = re.compile(pattern, re.DOTALL | re.MULTILINE)

    while True:
        m = re_compile.search(source)
        if m:
            start, end = m.span()
            if start:
                markdown = source[:start].strip()
                if markdown:
                    yield markdown
            yield m.group(1), m.group(3).strip(), m.group(2).strip()
            source = source[end:]
        else:
            markdown = source.strip()
            if markdown:
                yield markdown
            break

# def new_notebook(source: str,  metadata=None):
#     """
#     Convert a markdown source with `jupyter` fenced code into a markdown
#     source with `python` fenced code after executing the jupyter codes.
#
#     Parameters
#     ----------
#     source : str
#         Markdown source string.
#     language : str, optional
#         Fenced code language
#     metadata: dict, optional
#         Notebook metadata.
#     """
#     cells = []
#     for cell in fenced_code_splitter(source, 'jupyter'):
#         if isinstance(cell, str):
#             cell = nbformat.v4.new_markdown_cell(cell)
#             cells.append(cell)
#         else:
#             code, option = cell
#             cell = nbformat.v4.new_code_cell(code)
#             if option:
#                 options = [option.strip() for option in option.split(',')]
#             else:
#                 options = []
#             cell.metadata['pheasant'] = options
#             cells.append(cell)
#
#     if metadata is None:
#         metadata = {'language_info': {'name': language}}
#
#     metadata = NotebookNode()
#
#     return nbformat.v4.new_notebook(cells=cells, metadata=metadata)

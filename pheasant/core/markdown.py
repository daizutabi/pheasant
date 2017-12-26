import logging
import re

import nbformat

from pheasant.config import config
from pheasant.core.client import run_cell, select_kernel_name
from pheasant.core.notebook import convert as convert_notebook
from pheasant.core.notebook import update_cell_metadata

logger = logging.getLogger(__name__)
config = config['jupyter']


def convert(source: str):
    notebook = nbformat.v4.new_notebook(cells=list(cell_runner(source)),
                                        metadata={})
    markdown = convert_notebook(notebook)
    return markdown


def cell_runner(source: str):
    logger.info('Start markdown execution')
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

    Parameters
    ----------
    source : str
        Markdwn source string.
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
    If tuple, it is (language, code, option):

    ```<language> <option>
    <code>
    ```

    Parameters
    ----------
    source : str
        Markdwn source string.
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
#         Markdwn source string.
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

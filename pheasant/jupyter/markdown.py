import re

import nbformat

from ..utils import escaped_splitter, read_source
from .client import select_kernel_name
from .config import config
from .exporter import export, inline_export, run_and_export
from .preprocess import preprocess_code, preprocess_markdown


def convert(source: str):
    """Convert markdown string or file into markdown with running results.

    Parameters
    ----------
    source : str
        Markdown source string or filename

    Returns
    -------
    results : str
        Markdown source
    """
    config['run_counter'] = 0
    source = read_source(source)
    sources = [source.strip() for source in cell_runner(source)]
    return '\n\n'.join(source for source in sources if source)


def cell_runner(source: str):
    """Generate markdown string with outputs after running the source.

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    str
        Markdown string.
    """
    for splitted in fenced_code_splitter(source):
        if isinstance(splitted, str):
            yield preprocess_markdown(splitted)
        else:
            language, source, options = splitted
            kernel_name = select_kernel_name(language)
            cell = nbformat.v4.new_code_cell(source)
            cell.metadata['pheasant'] = {'options': options,
                                         'language': language}

            if 'inline' in options:
                cell.source = preprocess_code(cell.source)
                yield run_and_export(cell, inline_export, kernel_name)
            else:
                yield run_and_export(cell, export, kernel_name)


def fenced_code_splitter(source: str):
    """Generate splitted markdown and jupyter notebook cell from `source`.

    The type of generated value is str or tuple.
    If str, it is markdown.
    If tuple, it is (language, source, option). See below:

    source:
        <markdown>

        ```<language> <option1>, <option2>, ...
        ## <option>
        <source>
        ```
        ...

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    str or tuple
        Splitted str.
        If tuple, it is (language: str, source: str, options: list)
    """
    pattern_escape = r'^~~~$.*?^~~~$'
    patter_source = r'^```(\S+)([^\n.]*)\n(.*?)\n^```$'
    re_option = re.DOTALL | re.MULTILINE

    for splitted in escaped_splitter(patter_source, pattern_escape, source,
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
                source = splitted.group(3).strip()
                option = splitted.group(2).strip()

                # Phesant's special option syntax.
                if source.startswith('## '):
                    extra_option = source[3:source.find('\n')]
                    option = ' '.join([option, extra_option])
                options = [option.strip() for option in option.split(' ')]
                options = [option for option in options if option]
                yield language, source, options

import re

import nbformat

from ..utils import escaped_splitter, read_source
from .client import select_kernel_name
from .config import config
from .exporter import export, inline_export, run_and_export
from .preprocess import preprocess_code, preprocess_markdown
from ..markdown.convert import fenced_code_convert


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
    config['run_counter'] = 0  # used in the cache module.
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
                source = run_and_export(cell, export, kernel_name)
                yield from fenced_code_splitter_with_class(source)


def fenced_code_splitter_with_class(source: str):
    """Add class to <div> of fenced code block using codehilite extension.

    - Input:
        ```<language> .<class1> .<class2>
        <source>
        ```
    - Output:
        <div class='class1 class2 codehilite'> ..... </div>
    """
    for splitted in fenced_code_splitter(source):
        if isinstance(splitted, str):
            yield preprocess_markdown(splitted)
        else:
            language, source, options = splitted
            source = f'```{language}\n{source}\n```'
            cls = ' '.join(option[1:] for option in options
                           if option.startswith('.'))
            if not cls:
                yield source
            else:
                cls += ' codehilite'  # gives original 'codehilite' class.

            yield fenced_code_convert(source, cls)


def fenced_code_splitter(source: str, comment_option=True):
    """Generate splitted markdown and jupyter notebook cell from `source`.

    The type of generated value is str or tuple.
    If str, it is markdown.
    If tuple, it is (language, source, option). See below:
    If `comment_option` is True, the first line starting with `##` is
    assumed extra option.

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
    pattern_escape = r'^~~~\n(.*?)\n^~~~$'
    pattern_source = r'^```(\S+)([^\n]*)\n(.*?)\n^```$'
    re_option = re.DOTALL | re.MULTILINE

    for splitted in escaped_splitter(pattern_source, pattern_escape, source,
                                     option=re_option):
        if isinstance(splitted, str):
            match = re.match(pattern_escape, splitted, flags=re_option)
            if match:
                yield escaped_code(match)
            else:
                yield splitted
        else:
            language = splitted.group(1)
            if select_kernel_name(language) is None:
                yield splitted.group()
            else:
                source = splitted.group(3).strip()
                options = splitted.group(2).strip()

                # Phesant's special option syntax.
                if comment_option:
                    if source.startswith('## '):
                        extra_options = source[3:source.find('\n')]
                        options = ' '.join([options, extra_options])
                    options = [option.strip() for option in options.split(' ')]
                    options = [option for option in options if option]
                yield language, source, options


def escaped_code(match):
    """
    Input:
    ~~~
    ```<language> <options>
    <source>
    ```
    ~~~

    Outut:
    <div class="codehilite pheasant-jupyter-source"><pre> ... </pre></div>
    """
    source = ''.join(escaped_code_splitter(match))
    cls = 'pheasant-fenced-code pheasant-jupyter-source'
    source = f'<div class="codehilite {cls}"><pre>{source}</pre></div>'
    return source


def escaped_code_splitter(match):
    """Yield source wth codehilite from escaped fenced code."""
    for splitted in fenced_code_splitter(match.group(1), comment_option=False):
        if isinstance(splitted, str):
            yield splitted
            continue

        language, source, options = splitted
        source = f'```{language}\n{source}\n```'
        source = fenced_code_convert(source, only_code=True)
        source = (f'<span>```</span>{language} {options}\n'
                  f'{source}<span>```</span>')
        yield source

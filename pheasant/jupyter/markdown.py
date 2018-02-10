import re

import nbformat

from markdown import Markdown

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
                return source
            else:
                cls += ' codehilite'  # gives original 'codehilite' class.

            markdown = Markdown(extensions=['fenced_code', 'codehilite'],
                                extension_configs={'codehilite':
                                                   {'css_class': cls}})
            yield markdown.convert(source)


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
    pattern_escape = r'^~~~\n(.*?)\n^~~~$'
    pattern_source = r'^```(\S+)([^\n]*)\n(.*?)\n^```$'
    re_option = re.DOTALL | re.MULTILINE

    for splitted in escaped_splitter(pattern_source, pattern_escape, source,
                                     option=re_option):
        if isinstance(splitted, str):
            match = re.match(pattern_escape, splitted, flags=re_option)
            if match:
                yield escaped_fenced_code(match)
            else:
                yield splitted
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


def escaped_fenced_code(match) -> str:
    """Convert escaped fenced code into fenced code with codehilite.

    Input:
    ~~~
    ```<language> <options>
    <source>
    ```
    ~~~

    Outut:
    <div class="codehilite pheasant-jupyter-source"><pre> ... </pre></div>
    """
    language, source, options = next(fenced_code_splitter(match.group(1)))
    source = f'```{language}\n{source}\n```'
    markdown = Markdown(extensions=['fenced_code', 'codehilite'])
    source = markdown.convert(source)
    first_line = match.group(1).split('\n')[0]

    def replace(match):
        return f'<pre>{first_line}\n' + match.group(1) + '```</pre>'

    source = re.sub(r'<pre>(.*?)</pre>', replace, source, flags=re.DOTALL)
    source = source.replace('<div class="codehilite">',
                            '<div class="codehilite pheasant-jupyter-source">')
    return source

import re

from ..jupyter.client import select_kernel_name
from ..jupyter.preprocess import preprocess_markdown
from .converter import fenced_code_convert


def splitter(pattern: str, source: str, option=re.MULTILINE):
    """Generate splitted text from `source` by `pattern`."""
    re_compile = re.compile(pattern, option)

    while True:
        m = re_compile.search(source)
        if m:
            start, end = m.span()
            if start:
                yield source[:start]
            yield m
            source = source[end:]
        else:
            yield source
            break


def escaped_splitter(pattern: str,
                     pattern_escape: str,
                     source: str,
                     option=re.MULTILINE,
                     option_escape=re.MULTILINE | re.DOTALL):
    for splitted in splitter(pattern_escape, source, option_escape):
        if not isinstance(splitted, str):
            yield splitted.group()
        else:
            yield from splitter(pattern, splitted, option)


def escaped_splitter_join(pattern: str,
                          pattern_escape: str,
                          source: str,
                          option=re.MULTILINE,
                          option_escape=re.MULTILINE | re.DOTALL):
    """Join escaped string with normal string."""
    text = ''
    for splitted in escaped_splitter(pattern, pattern_escape, source,
                                     option, option_escape):
        if isinstance(splitted, str):
            text += splitted
        else:
            yield text
            yield splitted
            text = ''
    if text:
        yield text


def fenced_code_splitter(source: str, comment_option=True, strip=True):
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
                if strip:
                    splitted = splitted.strip()
                if splitted:
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


def escaped_code_splitter(match):
    """Yield source wth codehilite from escaped fenced code."""
    for splitted in fenced_code_splitter(match.group(1), comment_option=False,
                                         strip=False):
        if isinstance(splitted, str):
            yield splitted
        else:
            language, source, options = splitted
            source = f'```{language}\n{source}\n```'
            source = fenced_code_convert(source, only_code=True)
            source = (f'<span>```</span>{language} {options}\n'
                      f'{source}<span>```</span>')
            yield source


def escaped_code(match):
    """
    Input:
    ~~~
    ```<language> <options>
    <source>
    ```
    ~~~

    Outut:
    <div class="... pheasant-source"><pre> ... </pre></div>
    """
    source = ''.join(escaped_code_splitter(match))
    cls = 'pheasant-markdown pheasant-source'
    source = f'<div class="codehilite {cls}"><pre>{source}</pre></div>'
    return source

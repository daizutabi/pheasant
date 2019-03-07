"""A parse module for detecting valid pattern blocks."""

import re
from typing import Callable, Generator, List, Match, Optional, Tuple, Union


def splitter(
    pattern: str,
    source: str,
    option=re.MULTILINE
) -> Generator[Union[str, Match], None, None]:
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
            if source:
                yield source
            break


def escaped_splitter(
    pattern: str,
    pattern_escape: str,
    source: str,
    option=re.MULTILINE,
    option_escape=re.MULTILINE | re.DOTALL,
    escape_generator=None,
) -> Generator[Union[str, Match, Tuple[str, str, List[str]]], None, None]:
    for splitted in splitter(pattern_escape, source, option_escape):
        if not isinstance(splitted, str):
            if escape_generator:
                yield from escape_generator(splitted)
            else:
                yield splitted.group()
        else:
            yield from splitter(pattern, splitted, option)


def escaped_splitter_join(
    pattern: str,
    pattern_escape: str,
    source: str,
    option=re.MULTILINE,
    option_escape=re.MULTILINE | re.DOTALL
) -> Generator[Union[str, Match], None, None]:
    """Join escaped string with normal string."""
    text = ''
    for splitted in escaped_splitter(pattern, pattern_escape, source, option,
                                     option_escape, escape_generator=None):
        if isinstance(splitted, str):
            text += splitted
        elif isinstance(splitted, tuple):
            pass  # Never occur! Just for mypy.
        else:
            yield text
            yield splitted
            text = ''
    if text:
        yield text


def fenced_code_splitter(
        source: str,
        comment_option: bool = True,
        escape: Optional[Callable[[str, str, list], str]] = None,
) -> Generator[Union[str, Tuple[str, str, List[str]]], None, None]:
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

    from pheasant.jupyter.client import select_kernel_name
    pattern_escape = r'^~~~(\S*)(.*?)\n(.*?\n)~~~\n'
    pattern_source = r'^```(\S+)(.*?)\n(.*?\n)```\n'
    # pattern_escape = r'^~~~(\S*)(.*?)\n(.*?)\n~~~\n'
    # pattern_source = r'^```(\S+)(.*?)\n(.*?)\n```\n'
    re_option = re.DOTALL | re.MULTILINE

    for splitted in escaped_splitter(
            pattern_source, pattern_escape, source, option=re_option,
            escape_generator=escape_generator):
        if isinstance(splitted, tuple):
            yield splitted
        elif isinstance(splitted, str):
            if escape:
                match = re.match(pattern_escape, splitted, flags=re_option)
                if match:
                    yield escape(*from_match(match, False))
                    continue
            yield splitted
        else:
            language, code, options = from_match(splitted, comment_option)
            if select_kernel_name(language) is None and language != 'display':
                yield splitted.group()
            else:
                yield language, code, options


def from_match(match: Match, comment_option: bool
               ) -> Tuple[str, str, List[str]]:
    language = match.group(1)
    source = match.group(3)
    options = match.group(2)

    # Phesant's special option syntax.
    if comment_option and source.startswith('## '):
        extra_options = source[3:source.find('\n')]
        options = ' '.join([options, extra_options])

    options = [option.strip() for option in options.split(' ')]
    options = [option for option in options if option]
    return language, source, options


def escape_generator(
    match: Match
) -> Generator[Union[str, Tuple[str, str, List[str]]], None, None]:
    if match.group(1) != 'copy':
        yield match.group()
    else:
        source = match.group(3)
        yield f'~~~\n{source}~~~\n\n'
        yield from fenced_code_splitter(source)

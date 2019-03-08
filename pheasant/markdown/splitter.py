"""A parse module for detecting valid pattern blocks."""

import re
from typing import Callable, Iterator, List, Match, Optional, Tuple, Union

FenceTuple = Tuple[str, str, List[str]]  # language, code, options
Compound = Union[Match, FenceTuple, str]


def splitter(
    pattern: str, source: str, option=re.MULTILINE
) -> Iterator[Union[Match, str]]:
    """Generate splitted text from `source` by `pattern`."""
    re_compile = re.compile(pattern, option)

    while True:
        match = re_compile.search(source)
        if match:
            start, end = match.span()
            if start:
                yield source[:start]
            yield match
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
) -> Iterator[Compound]:
    for splitted in splitter(pattern_escape, source, option_escape):
        if isinstance(splitted, str):
            yield from splitter(pattern, splitted, option)
        else:
            if escape_generator:
                yield from escape_generator(splitted)
            else:
                yield splitted.group()


def escaped_splitter_join(
    pattern: str,
    pattern_escape: str,
    source: str,
    option=re.MULTILINE,
    option_escape=re.MULTILINE | re.DOTALL,
) -> Iterator[Union[Match, str]]:
    """Join escaped string with normal string."""
    text = ""
    for splitted in escaped_splitter(
        pattern, pattern_escape, source, option, option_escape, escape_generator=None
    ):
        if isinstance(splitted, str):
            text += splitted
        elif isinstance(splitted, tuple):
            pass  # Never occur! Just for mypy.
        else:
            yield text
            yield splitted
            text = ""
    if text:
        yield text


def fenced_code_splitter(
    source: str, escape: Optional[Callable[[str, str, list], str]] = None
) -> Iterator[Union[FenceTuple, str]]:
    """Generate splitted markdown and jupyter notebook cell from `source`.

    The type of generated value is str or tuple.
    If str, it is markdown.
    If tuple, it is (language, code, options). See below:

    source:
        <markdown>

        ```<language> <option1>, <option2>, ...
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

    pattern_escape = r"^~~~(\S*)(.*?)\n(.*?)\n~~~\n"
    pattern_source = r"^```(\S+)(.*?)\n(.*?)\n```\n"
    re_option = re.DOTALL | re.MULTILINE

    for splitted in escaped_splitter(
        pattern_source,
        pattern_escape,
        source,
        option=re_option,
        escape_generator=escape_generator,
    ):
        if isinstance(splitted, tuple):
            yield splitted
        elif isinstance(splitted, str):
            if escape:
                match = re.match(pattern_escape, splitted, flags=re_option)
                if match:
                    yield escape(*from_match(match))
                    continue
            yield splitted
        else:
            language, code, options = from_match(splitted)
            if select_kernel_name(language) is None and language != "display":
                yield splitted.group()
            else:
                yield language, code, options


def from_match(match: Match) -> FenceTuple:
    """Get (language:str, code:str, options:List[str]) from a Match object."""
    language, options, code = match.groups()
    options = [option.strip() for option in options.split(" ")]
    options = [option for option in options if option]
    return language, code, options


def escape_generator(match: Match) -> Iterator[Union[FenceTuple, str]]:
    """Generate a copy of escaped fenced code.

    Input:
        ~~~copy
        ```python inline
        print(1)
        ```
        ~~~

    Yields:
        1st: '~~~\n```python inline\nprint(1)\n```\n\n'
        2nd: ('python', 'print(1)', [inline])
    """
    if match.group(1) != "copy":
        yield match.group()
    else:
        code = match.group(3)
        yield f"~~~\n{code}\n~~~\n\n"
        yield from fenced_code_splitter(code + "\n")

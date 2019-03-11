"""A parse module for detecting valid pattern blocks."""

import re
from typing import (Callable, Iterator, List, Match, Optional, Pattern, Tuple,
                    Union)

from pheasant.markdown.config import ESCAPE_PATTEN, FENCED_CODE_PATTERN

FencedCodeTuple = Tuple[str, str, List[str]]  # language, code, options
Compound = Union[Match, FencedCodeTuple, str]


def splitter(pattern: Pattern, source: str) -> Iterator[Union[Match, str]]:
    """Generate splitted text from `source` by `pattern`."""
    while True:
        match = re.search(pattern, source)
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
    pattern: Pattern, pattern_escape: Pattern, source: str, escape_generator=None
) -> Iterator[Compound]:
    for splitted in splitter(pattern_escape, source):
        if isinstance(splitted, str):
            yield from splitter(pattern, splitted)
        else:
            if escape_generator:
                yield from escape_generator(splitted)
            else:
                yield splitted.group()


def escaped_splitter_join(
    pattern: Pattern, pattern_escape: Pattern, source: str
) -> Iterator[Union[Match, str]]:
    """Join escaped string with normal string."""
    text = ""
    for splitted in escaped_splitter(
        pattern, pattern_escape, source, escape_generator=None
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
) -> Iterator[Union[FencedCodeTuple, str]]:
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

    for splitted in escaped_splitter(
        FENCED_CODE_PATTERN, ESCAPE_PATTEN, source, escape_generator=escape_generator
    ):
        if isinstance(splitted, tuple):
            yield splitted
        elif isinstance(splitted, str):
            if escape:
                match = re.match(ESCAPE_PATTEN, splitted)
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


def from_match(match: Match) -> FencedCodeTuple:
    """Get (language:str, code:str, options:List[str]) from a Match object."""
    language, options, code = match.groups()
    options = [option.strip() for option in options.split(" ")]
    options = [option for option in options if option]
    return language, code, options


def escape_generator(match: Match) -> Iterator[Union[FencedCodeTuple, str]]:
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
    if match.group(1) == "copy":
        code = match.group(3)
        yield f"~~~\n{code}\n~~~\n\n"
        yield from fenced_code_splitter(code + "\n")
    else:
        yield match.group()

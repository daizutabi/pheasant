from typing import Generator, List

from pheasant.markdown.converter import fenced_code_convert
from pheasant.markdown.splitter import fenced_code_splitter


def convert(source: str) -> str:
    return ''.join(render(source))


def render(source: str) -> Generator[str, None, None]:
    """Add class to <div> of fenced code block using codehilite extension.

    - Input:
        ```<language> .<class1> .<class2>
        <source>
        ```
    - Output:
        <div class='class1 class2 codehilite'> ..... </div>
    """
    for splitted in fenced_code_splitter(source, escape=escaped_code):
        if isinstance(splitted, str):
            yield splitted
        else:
            yield hilite(*splitted)


def hilite(language: str,
           source: str,
           options: List[str],
           escaped: bool = False) -> str:
    source = f'```{language}\n{source}\n```'
    cls = ' '.join(option[1:] for option in options if option.startswith('.'))
    cls += ' codehilite'  # gives original 'codehilite' class.
    source = fenced_code_convert(source, cls=cls, only_code=escaped)
    if escaped:
        option = ' '.join(options)
        source = (f'<span>```</span>{language} {option}\n'
                  f'{source}<span>```</span>')
    return source


def escaped_code(language: str, source: str, options: List[str]) -> str:
    """
    Input:
    ~~~
    ```<language> <options>
    <source>
    ```
    ~~~

    Output:
    <div class="... pheasant-source"><pre> ... </pre></div>
    """
    if language:
        options += ['.pheasant-markdown', '.pheasant-code']
        return hilite(language, source, options)

    source = ''.join(escaped_code_splitter(source))
    cls = 'pheasant-markdown pheasant-source'
    source = f'<div class="codehilite {cls}"><pre>{source}</pre></div>'
    return source


def escaped_code_splitter(source: str) -> Generator[str, None, None]:
    """Yield source wth codehilite from escaped fenced code."""
    for splitted in fenced_code_splitter(source, comment_option=False):
        if isinstance(splitted, str):
            yield splitted
        else:
            yield hilite(*splitted, escaped=True) + '\n'

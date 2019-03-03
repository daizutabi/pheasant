from typing import Generator, List

from pheasant.markdown.converter import fenced_code_convert, markdown_convert
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
            yield html(*splitted)


def html(language: str, source: str, options: List[str],
         escaped: bool = False) -> str:
    """Convert fenced code into html with codehilite and <div> classes."""
    cls = ' '.join(option[1:] for option in options if option.startswith('.'))

    if language == 'display':  # special lang to display figures, tables, etc.
        if source.startswith('$$'):  # for latex
            source = f'<p>{source}</p>'
        else:
            source = markdown_convert(source)
        source = f'<div class="{cls}">\n{source}\n</div>\n'
        return source

    source = f'```{language}\n{source}\n```'
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
        options += ['.pheasant-fenced-code', '.pheasant-code']
        return html(language, source, options)

    source = ''.join(escaped_code_splitter(source))
    cls = 'pheasant-fenced-code pheasant-source'
    source = f'<div class="codehilite {cls}"><pre>{source}</pre></div>'
    return source


def escaped_code_splitter(source: str) -> Generator[str, None, None]:
    """Yield source wth codehilite from escaped fenced code."""
    for splitted in fenced_code_splitter(source, comment_option=False):
        if isinstance(splitted, str):
            yield splitted
        else:
            yield html(*splitted, escaped=True) + '\n'

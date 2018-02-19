from ..markdown.converter import fenced_code_convert
from ..markdown.splitter import fenced_code_splitter


def convert(source: str):
    return ''.join(render(source))


def render(source: str):
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


def hilite(language, source, options, escaped=False):
    source = f'```{language}\n{source}\n```'
    cls = ' '.join(option[1:] for option in options
                   if option.startswith('.'))
    cls += ' codehilite'  # gives original 'codehilite' class.
    source = fenced_code_convert(source, cls=cls, only_code=escaped)
    if escaped:
        option = ' '.join(options)
        source = (f'<span>```</span>{language} {option}\n'
                  f'{source}<span>```</span>')
    return source


def escaped_code(language, source, options):
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
    if language:
        options += ['.pheasant-markdown', '.pheasant-code']
        return hilite(language, source, options)

    source = ''.join(escaped_code_splitter(source))
    cls = 'pheasant-markdown pheasant-source'
    source = f'<div class="codehilite {cls}"><pre>{source}</pre></div>'
    return source


def escaped_code_splitter(source):
    """Yield source wth codehilite from escaped fenced code."""
    for splitted in fenced_code_splitter(source, comment_option=False):
        if isinstance(splitted, str):
            yield splitted
        else:
            yield hilite(*splitted, escaped=True)

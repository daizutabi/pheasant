from typing import Generator, List

from pheasant.markdown.converter import markdown_convert
from pheasant.markdown.splitter import fenced_code_splitter


def convert(source: str) -> str:
    return ''.join(render(source))


def render(source: str) -> Generator[str, None, None]:
    """Add class to <div> of fenced code block.

    - Input:
        ```[language] .[class1] .[class2]
        [source]
        ```

    - Output:
        <div class='[class1] [class2]'>
          <pre><code="[language]">[source]</code></pre>
        </div>
    """
    for splitted in fenced_code_splitter(source, escape=escaped_code):
        if isinstance(splitted, str):
            yield splitted
        else:
            yield div(*splitted)


def div(language: str, source: str, options: List[str],
        escaped: bool = False) -> str:
    """Convert fenced code into html with <div> classes."""
    cls = ' '.join(option[1:] for option in options if option.startswith('.'))

    if language == 'display':  # special lang to display figures, tables, etc.
        if source.startswith('$$'):  # for latex
            source = f'<p>{source}</p>'
        else:
            source = markdown_convert(source)
        source = f'<div class="{cls}">\n{source}\n</div>\n'
        return source

    source = f'```{language}\n{source}```'  # No new line after {source}.
    source = markdown_convert(source)
    if cls:
        source = f'<div class="{cls}">\n{source}\n</div>\n'
    else:
        source = f'<div>\n{source}\n</div>\n'

    return source


def escaped_code(language: str, source: str, options: List[str]) -> str:
    """
    Input:
    ~~~
    ```[language] [options..]
    [source]
    ```
    ~~~

    Output:
    <div class="... pheasant-source"><pre> ... </pre></div>
    """
    language = language or 'markdown'
    if options:
        cls = ' '.join([option[1:] for option in options
                        if option.startswith('.')])
    else:
        cls = 'pheasant-fenced-code pheasant-source'

    source = (f'<div class="{cls}">\n<pre><code class="{language}">'
              f'{source}</code></pre>\n</div>\n')
    return source

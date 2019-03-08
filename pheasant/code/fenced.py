from typing import Iterator, List

from pheasant.markdown.converter import markdown_convert
from pheasant.markdown.splitter import fenced_code_splitter


def convert(source: str) -> str:
    return "".join(render(source))


def render(source: str) -> Iterator[str]:
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


def div(language: str, code: str, options: List[str]) -> str:
    """Convert fenced code into html with <div> classes."""
    cls = " ".join(option[1:] for option in options if option.startswith("."))

    if language == "display":  # special lang to display figures, tables, etc.
        if code.startswith("$$"):  # for latex
            code = f"<p>{code}</p>"
        else:
            code = markdown_convert(code)
        code = f'<div class="{cls}">\n{code}</div>\n'
        return code

    code = f"```{language}\n{code}\n```"
    code = markdown_convert(code)
    if cls:
        code = f'<div class="{cls}">\n{code}</div>\n'
    else:
        code = f"<div>\n{code}</div>\n"

    return code


def escaped_code(language: str, source: str, options: List[str]) -> str:
    """
    Input:
    ~~~[language] [options..]

    <raw source>

    ~~~

    Output:
    <div class="... pheasant-source"><pre> ... </pre></div>
    """
    language = language or "markdown"
    if options:
        cls = " ".join([option[1:] for option in options if option.startswith(".")])
    else:
        cls = "pheasant-fenced-code pheasant-source"

    escaped_backquotes = '<span class="pheasant-backquote">```</span>'
    source = source.replace("```", escaped_backquotes)
    source = (
        f'<div class="{cls}">\n<pre><code class="{language}">'
        f"{source}</code></pre></div>\n"
    )
    return source

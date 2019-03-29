import re
from dataclasses import field
from typing import Iterator

from pheasant.core.renderer import Renderer
from pheasant.script.formatter import format_source
from pheasant.script.splitter import DOCSTRING_PATTERN, split

COMMENT_PATTERN = re.compile(r"^#\s?", re.MULTILINE)


class Comment(Renderer):
    max_line_length: int = 0
    option: str = field(default="", init=False)

    HEADER_PATTERN = r"^(?P<source>#.*?\n)"
    FENCED_CODE_PATTERN = r"^(?P<mark>~{3,}|`{3,}).*?\n(?P=mark)\n"

    def init(self):
        self.register(Comment.HEADER_PATTERN, self.render_header)
        self.register(Comment.FENCED_CODE_PATTERN, self.render_fenced_code)

    def render_header(self, context, splitter, parser) -> Iterator[str]:
        yield context["_source"]

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        markdown = context["mark"] + "markdown\n"
        if context["_source"].startswith(markdown) and self.max_line_length == 0:
            yield context["_source"][len(markdown) : -len(context["mark"]) - 1]
        else:
            yield context["_source"]

    def decorate(self, cell) -> None:
        if cell.match is None:
            if self.max_line_length == 0 and cell.source.startswith("-"):
                cell.output = ""
                self.option = " " + cell.source[1:-1]
            else:
                cell.output = format_source(cell.source, self.max_line_length)


def delete_sharp(source: str) -> str:
    return COMMENT_PATTERN.sub("", source)


def add_sharp(source: str) -> str:
    gen = ("# " + line if line else line for line in source.split("\n")[:-1])
    return "\n".join(gen) + "\n"


class Script(Renderer):
    comment: Comment = field(default_factory=Comment, init=False)

    def init(self):
        self.register(r"^(?P<source>.+)", self.render_entire)

    def render_entire(self, context, splitter, parser) -> Iterator[str]:
        for kind, source in split(context["source"]):
            if kind == "Comment":
                output = self.comment.parse(delete_sharp(source))
                if self.comment.max_line_length > 0:
                    output = add_sharp(output)
                yield output
            elif kind == "Code":
                if self.comment.max_line_length == 0:
                    yield f"```python{self.comment.option}\n{source}```\n"
                    self.comment.option = ""
                else:
                    yield source
            elif kind == "Docstring":
                match = DOCSTRING_PATTERN.match(source)
                quote, source = match.groups()  # type: ignore
                markdown = "markdown\n"
                if source.startswith(markdown):
                    source = source[len(markdown) :]
                    if not source.endswith("\n"):
                        source = source + "\n"
                    source = add_sharp(source)
                    output = parser.parse(source)
                    if self.comment.max_line_length > 0:
                        output = delete_sharp(output)
                else:
                    markdown = ""
                    output = source

                if self.comment.max_line_length > 0:
                    yield f"{quote}{markdown}{output}{quote}\n"
                elif markdown:
                    yield "\n" + output + "\n"
                else:
                    source = source.strip()
                    yield (
                        '\n<div class="pheasant-fenced-code"><div class="docstring">'
                        f'<pre><code class="text">{source}'
                        "</code></pre></div></div>\n\n"
                    )
            else:
                yield source

    def convert(self, source: str, max_line_length=88):
        if max_line_length:
            max_line_length -= 2
        self.comment.max_line_length = max_line_length
        nl = "\r\n" if "\r\n" in source else "\n"
        if nl != "\n":
            source = source.replace(nl, "\n")
        output = self.parse(source)
        if nl != "\n":
            output = output.replace("\n", nl)
        return output

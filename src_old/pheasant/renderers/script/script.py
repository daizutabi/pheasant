import re
from dataclasses import field
from typing import Iterator

from pheasant.core.renderer import Renderer
from pheasant.renderers.script.formatter import format_source
from pheasant.renderers.script.splitter import DOCSTRING_PATTERN, split

COMMENT_PATTERN = re.compile(r"^#\s?", re.MULTILINE)


class Comment(Renderer):
    max_line_length: int = 0
    option: str = field(default="", init=False)

    HEADER_PATTERN = r"^(?P<prefix>#+.*? +?)(?P<title>.*?\n)"
    FENCED_CODE_PATTERN = r"^(?P<mark>~{3,}|`{3,}).*?\n(?P=mark)\n"
    LIST_PATTERN = r"^ *?(?P<prefix>[-\+\*]|\d+\.) +.*?\n"
    ADMONITION_PATTERN = r"^!!! .*(?!^    )"

    def init(self):
        self.register(Comment.HEADER_PATTERN, self.render_header)
        self.register(Comment.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Comment.LIST_PATTERN, self.render_list)
        self.register(Comment.ADMONITION_PATTERN, self.render_admonition)

    def render_header(self, context, splitter, parser) -> Iterator[str]:
        prefix, title = context["prefix"], context["title"]

        def header():
            title_ = format_source(title, self.max_line_length - len(prefix))
            return add_prefix(title_, prefix)

        for cell in splitter:
            if cell._render != self.render_header or cell.context["prefix"] != prefix:
                yield header()
                splitter.send(cell.source)
                return
            else:
                title += cell.context["title"]
        yield header()

    def render_fenced_code(self, context, splitter, parser) -> Iterator[str]:
        markdown = context["mark"] + "markdown\n"
        if context["_source"].startswith(markdown) and self.max_line_length == 0:
            yield context["_source"][len(markdown) : -len(context["mark"]) - 1]
        else:
            yield context["_source"]

    def render_list(self, context, splitter, parser) -> Iterator[str]:
        yield context["_source"]

    def render_admonition(self, context, splitter, parser) -> Iterator[str]:
        lines = context["_source"].strip().split("\n")
        header = lines[0]
        content = "\n".join(line[4:] for line in lines[1:]) + "\n"
        content = format_source(content, self.max_line_length - 4)
        lines = content.strip().split("\n")
        content = "\n".join("    " + line for line in lines) + "\n"
        output = "\n".join([header, content])
        yield output

    def decorate(self, cell) -> None:
        if cell.match is None:
            if self.max_line_length == 0 and cell.source.startswith("-"):
                cell.output = ""
                self.option = " " + cell.source[1:-1].strip()
            else:
                cell.output = format_source(cell.source, self.max_line_length)


def delete_prefix(source: str) -> str:
    return COMMENT_PATTERN.sub("", source)


def add_prefix(source: str, prefix: str = "# ") -> str:
    gen = (prefix + line if line else line for line in source.split("\n")[:-1])
    return "\n".join(gen) + "\n"


class Script(Renderer):
    comment: Comment = field(default_factory=Comment, init=False)

    def init(self):
        self.register(r"^(?P<source>.+)", self.render_entire)

    def render_entire(self, context, splitter, parser) -> Iterator[str]:
        for kind, source in split(context["source"]):
            if kind == "Comment":
                if source.startswith("# __break") and self.comment.max_line_length == 0:
                    return
                output = self.comment.parse(delete_prefix(source))
                if self.comment.max_line_length > 0:
                    output = add_prefix(output)
                yield output
            elif kind == "Code":
                if self.comment.max_line_length == 0:
                    source = source.strip()
                    source = f"```python{self.comment.option}\n{source}\n```\n"
                    yield source
                    self.comment.option = ""
                else:
                    yield source
            elif kind == "Cell":
                if self.comment.max_line_length > 0:
                    yield source
            elif kind == "Docstring":
                match = DOCSTRING_PATTERN.match(source)
                quote, source = match.groups()  # type: ignore
                if source.startswith("markdown\n") or source.startswith("md\n"):
                    index = source.index("\n")
                    markdown, source = source[: index + 1], source[index + 1 :]
                    if not source.endswith("\n"):
                        source = source + "\n"
                    source = add_prefix(source)
                    output = parser.parse(source)
                    if self.comment.max_line_length > 0:
                        output = delete_prefix(output)
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

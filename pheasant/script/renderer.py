from dataclasses import field
from typing import Iterator

from pheasant.core.renderer import Renderer
from pheasant.script.formatter import format_comment
from pheasant.script.splitter import split


class Comment(Renderer):
    max_line_length: int = 0
    option: str = ""

    HEADER_PATTERN = r"^(?P<source>#\s*#.*?\n)"
    FENCED_CODE_PATTERN = r"^#\s*(?P<mark>~{3,}|`{3,}).*?\n#\s*(?P=mark)\n"

    def __post_init__(self):
        super().__post_init__()
        self.register(Comment.HEADER_PATTERN, self.render_escape, "comment__header")
        pattern = Comment.FENCED_CODE_PATTERN
        self.register(pattern, self.render_escape, "comment__fenced_code")

    def render_escape(self, context, splitter, parser) -> Iterator[str]:
        if self.max_line_length == 0:
            yield format_comment(context["_source"], -1)  # Just remove "# ".
        else:
            yield context["_source"]

    def decorate(self, cell) -> None:
        if cell.match is None and self.max_line_length != -1:
            if self.max_line_length == 0 and cell.source.startswith("# -"):
                cell.output = ""
            else:
                cell.output = format_comment(cell.source, self.max_line_length)


class Script(Renderer):
    comment: Comment = field(default_factory=Comment)

    def __post_init__(self):
        super().__post_init__()
        self.register(r"^(?P<source>.+)", self.render_entire)

    def render_entire(self, context, splitter, parser) -> Iterator[str]:
        for kind, source in split(context["source"]):
            if kind == "Comment":
                yield self.comment.parse(source)
            elif kind == "Code":
                if self.comment.max_line_length == 0:
                    yield f"```python\n{source}```\n"
                else:
                    yield source
            else:
                yield source

    def convert(self, source: str, max_line_length=88):
        self.comment.max_line_length = max_line_length
        nl = "\r\n" if "\r\n" in source else "\n"
        if nl != "\n":
            source = source.replace(nl, "\n")
        output = self.parse(source)
        if nl != "\n":
            output = output.replace("\n", nl)
        return output

from typing import Any, Dict, Iterable, List, Match, Optional

from pheasant.core.parser import Parser
from pheasant.core.renderer import Config, Context, Renderer


class Code(Renderer):

    FENCED_CODE_PATTERN = (
        r"^(?P<mark>~{3,})(?P<language>\w+) ?(?P<option>.*?)\n"
        r"(?P<source>.*?)\n(?P=mark)\n"
    )
    INLINE_CODE_PATTERN = r"^(?P<header>#?)!\[(?P<language>\w+?)\]\((?P<source>.+?)\)\n"

    def __init__(self, config: Optional[Config] = None):
        super().__init__(config)
        self.register(Code.FENCED_CODE_PATTERN, self.render_fenced_code)
        self.register(Code.INLINE_CODE_PATTERN, self.render_inline_code)
        self.set_template("fenced_code")

    def render_fenced_code(self, context: Context, parser: Parser) -> Iterable[str]:
        if context["language"] == "copy":
            context["language"] = "markdown"
            copy = True
        else:
            copy = False
        yield self.render(self.config["fenced_code_template"], context)

        if copy:
            yield "\n"  # important.
            yield from parser.parse(context["source"] + "\n")

    def render_inline_code(self, context: Context, parser: Parser) -> Iterable[str]:
        if context["language"] == 'file':
            # example
            context["source"] = 'abc'
            context["language"] == 'python'
            yield from self.render_fenced_code(context, parser)
        else:


            yield "abc"
        # context["code"] = preprocess_inline_code(context["code"])
        # yield self.render(self.config["inline_code_template"], context)

    def render(self, template, context: Dict[str, Any]) -> str:
        context.update(config=self.config)
        return template.render(**context)

from typing import Iterator

from pheasant.core.renderer import Renderer
from pheasant.script.formatter import Formatter
from pheasant.script.splitter import splitter as splitter_


class Script(Renderer):

    PYTHON_CODE_PATTERN = r"^(?P<source>.+)"  # Entire source!

    def __post_init__(self):
        super().__post_init__()
        self.register(Script.PYTHON_CODE_PATTERN, self.render_script_code)

    def render_script_code(self, context, splitter, parser) -> Iterator[str]:
        if not context["source"].endswith('\n'):
            context["source"] += "\n"
        formatter = Formatter(context["source"])
        for cell_type, begin, end in splitter_(context["source"]):
            yield formatter(cell_type, begin, end) + "\n"

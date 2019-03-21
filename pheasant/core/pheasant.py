from dataclasses import field
from typing import Dict, Iterator, List

from pheasant.code.renderer import Code
from pheasant.core.converter import Converter
from pheasant.core.decorator import Decorator
from pheasant.core.page import Page
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Anchor, Header
from pheasant.python.renderer import Python


class Pheasant(Converter):
    python: Python = field(default_factory=Python, init=False)
    jupyter: Jupyter = field(default_factory=Jupyter, init=False)
    header: Header = field(default_factory=Header, init=False)
    code: Code = field(default_factory=Code, init=False)
    anchor: Anchor = field(default_factory=Anchor, init=False)
    decorator: Decorator = field(default_factory=Decorator, init=False)
    pages: Dict[str, Page] = field(default_factory=dict, init=False)

    def __post_init__(self):
        super().__post_init__()
        self.anchor.header = self.header
        self.register("script", [self.python])
        self.register("main", [self.header, self.jupyter, self.code], self.decorator)
        self.register("link", [self.anchor])

        self.decorator.name = "pheasant"
        self.decorator.register("surround", [self.header, self.jupyter, self.code])
        self.setup()

    def convert_from_files(self, paths: List[str], message=None) -> List[str]:
        self.reset()
        for path in paths:
            self.jupyter.reset()  # Reset extra_resources
            self.header.abs_src_path = path
            if path.endswith(".py"):
                if message:
                    message(f"Converting Python script: {path}")
                self.convert_from_file(path, ["script", "main"])
            else:
                if message:
                    message(f"Converting Markdown: {path}")
                self.convert_from_file(path, "main")
            self.pages[path].meta["extra_resources"] = self.jupyter.meta[
                "extra_resources"
            ]
        for path in paths:
            self.anchor.abs_src_path = path
            if message:
                message(f"Interlinking: {path}")
            self.convert_from_output(path, "link")
        return [self.pages[path].output for path in paths]

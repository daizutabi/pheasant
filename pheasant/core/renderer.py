import importlib
import os
from dataclasses import field
from typing import Any, Dict, List, Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pheasant.core.base import Base, get_render_name
from pheasant.core.parser import Parser, Render  # Render is type, not class


class Renderer(Base):
    patterns: Dict[str, str] = field(default_factory=dict, init=False)
    renders: Dict[str, Render] = field(default_factory=dict, init=False)
    _parser: Optional[Parser] = field(default=None, init=False)

    def __post_repr__(self):
        return len(self.renders)

    def register(self, pattern: str, render: Render, render_name: str = "") -> None:
        if not render_name:
            render_name = get_render_name(render)
        self.patterns[render_name] = pattern
        self.renders[render_name] = render

    @property
    def parser(self) -> Parser:
        if self._parser is None:
            self.parser = Parser()
        return self._parser  # type: ignore

    @parser.setter
    def parser(self, parser: Parser) -> None:
        for render_name, pattern in self.patterns.items():
            render = self.renders[render_name]
            parser.register(pattern, render, render_name)
        self._parser = parser

    def setup(self) -> None:
        """Called once on build."""
        pass

    def reset(self) -> None:
        """Called per page."""
        pass

    def set_template(
        self, templates: Union[str, List[str]], directory: str = ""
    ) -> None:
        if not directory:
            module = importlib.import_module(self.__module__)
            directory = os.path.join(os.path.dirname(module.__file__), "templates")
        loader = FileSystemLoader([directory])
        env = Environment(loader=loader, autoescape=select_autoescape(["jinja2"]))
        if isinstance(templates, str):
            templates = [templates]
        for template in templates:
            if "." not in template:
                template = f"{template}.jinja2"
            key = f"{template}_template"
            self.config[key] = env.get_template(template)

    def render(self, template: str, context: Dict[str, Any], **kwargs) -> str:
        return self.config[template + "_template"].render(
            context, config=self.config, **kwargs
        )

    def parse(self, source: str) -> str:
        return self.parser.parse(source, decorate=self.decorate)

    def decorate(self, cell):
        """Decorate cell.output after parse.

        Overwritten by subclass."""
        pass

import importlib
import os
from dataclasses import field
from typing import Any, Dict, List, Optional, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape

from pheasant.core.base import Base, get_render_name
from pheasant.core.parser import Parser, Render  # Render is type, not class


class Renderer(Base):
    patterns: Dict[str, str] = field(default_factory=dict)
    renders: Dict[str, Render] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self._parser: Optional[Parser] = None

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

    def set_template(self, names: Union[str, List[str]] = "") -> None:
        module = importlib.import_module(self.__module__)
        directory = os.path.join(os.path.dirname(module.__file__), "templates")
        if isinstance(names, str):
            names = [names]
        for name in names:
            template = f"{name}_template"
            template_file = f"{name}_template_file"
            if template_file in self.config:
                path = self.config[template_file]
            else:
                path = os.path.join(directory, f"{name}.jinja2")
            directory, path = os.path.split(os.path.abspath(path))
            loader = FileSystemLoader([directory])
            env = Environment(loader=loader, autoescape=select_autoescape(["jinja2"]))
            self.config[template] = env.get_template(path)

    def render(self, template: str, context: Dict[str, Any], **kwargs):
        return self.config[template + "_template"].render(
            context, config=self.config, **kwargs
        )

    def parse(self, source: str) -> str:
        return self.parser.parse(source, decorate=self.decorate)

    def decorate(self, cell):
        """Decorate cell.output after parse.

        Overwritten by subclass."""
        pass

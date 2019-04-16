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
    _src_path: str = ""

    def __post_init__(self):
        super().__post_init__()
        self.init()

    def __post_repr__(self):
        return len(self.renders)

    def init(self) -> None:
        """Called from __post_init__."""
        pass

    def reset(self) -> None:
        """Called per page."""
        pass

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

    @property
    def src_path(self) -> str:
        return self._src_path

    @src_path.setter
    def src_path(self, src_path: str) -> None:
        self._src_path = src_path

    def set_template(self, names: Union[str, List[str]], directory: str = ".") -> None:
        module = importlib.import_module(self.__module__)
        default = os.path.join(os.path.dirname(module.__file__), "templates")
        loader = FileSystemLoader([directory, default])
        env = Environment(loader=loader, autoescape=select_autoescape(["jinja2"]))
        names = [names] if isinstance(names, str) else names
        for name in names:
            if ":" in name:
                name, path = name.split(":")
            else:
                path = name
            template = f"{path}.jinja2" if "." not in name else name
            self.config[f"{name}_template"] = env.get_template(template)

    def render(self, name: str, context: Dict[str, Any], **kwargs) -> str:
        template = self.config[f"{name}_template"]
        return template.render(context, config=self.config, **kwargs)

    def parse(self, source: str) -> str:
        return self.parser.parse(source, decorate=self.decorate)

    def decorate(self, cell):
        """Decorate cell.output after parse.

        Overwritten by subclass."""
        pass

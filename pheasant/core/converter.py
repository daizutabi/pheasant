from collections import OrderedDict
from dataclasses import field
from typing import Any, Callable, Dict, Iterable, Iterator, List

from pheasant.core.base import Base, Page
from pheasant.core.decorator import monitor
from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer


class Converter(Base):
    parsers: Dict[str, Parser] = field(default_factory=OrderedDict)
    renderers: Dict[str, List[Renderer]] = field(default_factory=dict)
    pages: Dict[str, Page] = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.init()

    def __post_repr__(self):
        return ", ".join(f"'{name}'" for name in self.parsers)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.parsers[item]
        elif isinstance(item, tuple):
            renderers = self.renderers[item[0]]
            for renderer in renderers:
                if renderer.name == item[1]:
                    return renderer
            else:
                raise KeyError

    def renderer_iter(self) -> Iterator[Renderer]:
        for renderers in self.renderers.values():
            yield from renderers

    def update_config(self, config: Dict[str, Any]):
        for renderer in self.renderer_iter():
            if renderer.name in config and isinstance(config[renderer.name], dict):
                renderer._update("config", config[renderer.name])

    def init(self) -> None:
        """Called from __post_init__."""
        pass

    def reset(self):
        for renderer in self.renderer_iter():
            renderer.reset()
        self.pages = {}

    def register(self, renderers: Iterable[Renderer], name: str = "default"):
        """Register renderer's processes

        Parameters
        ----------
        renderers
            List of Renderer
        name
            The name of Parser
        """
        if name in self.parsers:
            raise ValueError(f"Duplicated parser name '{name}'")
        parser = Parser(name)  # type: ignore
        for renderer in renderers:
            renderer.parser = parser
        self.parsers[name] = parser
        self.renderers[name] = list(renderers)

    def parse(self, source: str, name: str = "default") -> str:
        """Parse source text.

        Parameters
        ----------
        source
            The source text to be parsed.
        name
            Parser name to be used.

        Returns
        -------
        Parsed output text.
        """
        return self.parsers[name].parse(source)

    def get_page(self, path: str) -> Page:
        if path not in self.pages:
            self.pages[path] = Page(path).read()

        return self.pages[path]

    def apply(self, path: str, func: Callable[[Page], None]):
        page = self.get_page(path)
        func(page)

    def __enter__(self):
        for renderer in self.renderers:
            renderer.enter()

    def __exit__(self, exc_type, exc_value, traceback):
        for renderer in self.renderers:
            renderer.exit()

    @monitor(format=True)
    def convert(self, path: str, name: str = "default") -> str:
        """Convert source file.

        Parameters
        ----------
        path
            The source path to be converted.
        name
            Parser name to be used.

        Returns
        -------
        Converted output text.
        """
        page = self.get_page(path)

        for renderer in self.renderers[name]:
            renderer.page = page
            renderer.enter()

        page.source = self.parse(page.source, name)

        for renderer in self.renderers[name]:
            renderer.exit()

        return page.source

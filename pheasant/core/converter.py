import io
import re
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import (Any, Callable, Dict, Iterable, Iterator, List, Optional,
                    Union)

from pheasant.core.base import Base
from pheasant.core.decorator import monitor
from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer


@dataclass
class Page:
    markdown: str
    extra_html: str = ""


COMMENT_PATTERN = re.compile("<!--.*?-->", re.DOTALL)


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

    def register(self, name: str, renderers: Union[Renderer, Iterable[Renderer]]):
        """Register renderer's processes

        Parameters
        ----------
        name
            The name of Parser
        renderers
            List of Renderer's instance or name of Renderer
        """
        if name in self.parsers:
            raise ValueError(f"Duplicated parser name '{name}'")
        parser = Parser(name)  # type: ignore
        if isinstance(renderers, Renderer):
            renderers = [renderers]
        for renderer in renderers:
            renderer.parser = parser
        self.parsers[name] = parser
        self.renderers[name] = list(renderers)

    def convert(
        self, source: str, names: Union[str, Iterable[str], None] = None
    ) -> str:
        """Convert source text.

        Parameters
        ----------
        source
            The source text to be converted.
        names
            Parser names to be used. If not specified. all of the registered
            parsers will be used.

        Returns
        -------
        Converted output text.
        """
        if isinstance(names, str):
            names = [names]
        for name in names or self.parsers:
            source = self.parsers[name].parse(source)

        return source

    def get_page(self, path: str) -> Page:
        if path not in self.pages:
            with io.open(path, "r", encoding="utf-8-sig", errors="strict") as f:
                source = f.read()
            source = COMMENT_PATTERN.sub("", source)
            self.pages[path] = Page(source)

        return self.pages[path]

    def apply(self, path: str, func: Callable[[Page], None]):
        page = self.get_page(path)
        func(page)

    @monitor(format=True)
    def convert_from_file(
        self, path: str, names: Union[str, Iterable[str], None] = None
    ) -> str:
        """Convert source text from file.

        Parameters
        ----------
        path
            The source path to be converted.
        names
            Parser names to be used. If not specified. all of the registered
            parsers will be used.
        copy
            If True, the page source is copied from the converted output after
            conversion.

        Returns
        -------
        Converted output text.
        """
        if isinstance(names, str):
            names = [names]
        for name in names or self.renderers:
            for renderer in self.renderers[name]:
                renderer.src_path = path

        page = self.get_page(path)
        page.markdown = self.convert(page.markdown, names)
        return page.markdown

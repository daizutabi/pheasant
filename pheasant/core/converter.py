import datetime
import os
import time
from collections import OrderedDict
from contextlib import contextmanager
from dataclasses import field
from typing import Any, Dict, Iterable, Iterator, List

from pheasant.core.base import Base
from pheasant.core.page import Page
from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer
from pheasant.utils.time import format_timedelta_human


class Log:
    pass


class Converter(Base):
    parsers: Dict[str, Parser] = field(default_factory=OrderedDict)
    renderers: Dict[str, List[Renderer]] = field(default_factory=dict)
    pages: Dict[str, Page] = field(default_factory=dict)
    dirty: bool = False
    log: Log = field(default_factory=Log, init=False)

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
        """Yield registered renderers."""
        for renderers in self.renderers.values():
            yield from renderers

    def update_config(self, config: Dict[str, Any]):
        for renderer in self.renderer_iter():
            if renderer.name in config and isinstance(config[renderer.name], dict):
                renderer._update("config", config[renderer.name])

    def init(self) -> None:
        """Called from __post_init__."""
        pass

    def start(self):
        for renderer in self.renderer_iter():
            renderer.start()
        if not self.dirty:
            self.pages.clear()

    def register(self, renderers: Iterable[Renderer], name: str = "default"):
        """Register renderer's processes to a parser.

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
        """Parse a source text.

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

    def convert_by_name(self, path: str, name: str) -> str:
        """Convert a source file with a named parser.

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
        if path not in self.pages:
            self.pages[path] = Page(path).read()

        page = self.pages[path]

        for renderer in self.renderers[name]:
            renderer.page = page
            renderer.enter()

        try:
            source = self.parse(page.source, name)
        except Exception:
            raise
        else:
            page.source = source
            page.converted_time = time.time()

        for renderer in self.renderers[name]:
            renderer.exit()

        return page.source

    def _convert(self, path: str) -> str:
        """Convert a source file with sequntial parsers.

        Parameters
        ----------
        path
            The source path to be converted.

        Returns
        -------
        Converted output text.
        """
        return self.convert_by_name(path, "default")

    def convert(self, path: str) -> str:
        """Convert a source file with sequntial parsers.

        Parameters
        ----------
        path
            The source path to be converted.

        Returns
        -------
        Converted output text.
        """
        if self.dirty and path in self.pages:
            if self.pages[path].converted_time > os.stat(path).st_mtime:
                return self.pages[path].source
            else:
                self.pages.pop(path)

        return self._convert(path)

    def _convert_from_files(self, paths: Iterable[str]) -> List[str]:
        return ["Not implemented" for path in paths]

    def convert_from_files(self, paths: Iterable[str]) -> List[str]:
        with elapsed_time(self.log):
            return self._convert_from_files(paths)


@contextmanager
def elapsed_time(log):
    log.start = datetime.datetime.now()
    try:
        yield
    finally:
        log.end = datetime.datetime.now()
        log.elapsed = log.end - log.start
        time = format_timedelta_human(log.elapsed)
        log.info = f"Elapsed time: {time}"

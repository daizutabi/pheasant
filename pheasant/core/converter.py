import codecs
import importlib
from functools import partial
from typing import Callable, Dict, Iterable, List, Optional, Union

from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer


class Converter:
    def __init__(self):
        self.parsers: Dict[str, Parser] = {}
        self.renderers: Dict[str, List[Renderer]] = {}
        self.names: List[str] = []

    def __repr__(self):
        run = "->".join(f"'{name}'" for name in self.names)
        return f"<{self.__class__.__qualname__}[{run}])>"

    def __len__(self):
        return len(self.names)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.names[item]
        elif isinstance(item, str):
            return self.renderers[item]
        elif isinstance(item, tuple):
            if len(item) == 2:
                if isinstance(item[1], str):
                    return getattr(self, item[1] + "s")[item[0]]
                else:
                    return self.renderers[item[0]][item[1]]
            else:
                return self.__getitem__(item[:2])[item[2]]
        raise IndexError("converter index out of range")

    def register(
        self,
        name: str,
        renderers: Union[Union[Renderer, str], Iterable[Union[Renderer, str]]],
    ):
        """Register renderer's processes

        Parameters
        ----------
        name
            The name of Parser
        renderers
            List of Renderer's instance or name of Renderer
        """
        if not isinstance(renderers, Iterable):
            renderers = [renderers]
        if name in self.parsers:
            raise ValueError
        self.names.append(name)
        parser = Parser()
        self.parsers[name] = parser
        self.renderers[name] = [
            resolve_renderer(renderer) if isinstance(renderer, str) else renderer
            for renderer in renderers
        ]
        for renderer in self.renderers[name]:
            for pattern, render in renderer.renders.items():
                parser.register(pattern, render)

    def convert(
        self, source: str, names: Optional[Union[str, Iterable[str]]] = None
    ) -> str:
        """Convert source text.

        Parameters
        ----------
        source
            The text string to be converted.
        names
            Parser names to be used. If not specified. all of the registered
            parsers will be used.

        Returns
        -------
        Converted source text.
        """
        if isinstance(names, str):
            names = [names]
        names = names or self.names
        for name in names:
            parser = self.parsers[name]
            source = "".join(parser.parse(source))

        return source

    def convert_from_file(
        self, path: str, names: Optional[Iterable[str]] = None
    ) -> str:
        """Convert source text from file.

        Parameters
        ----------
        source
            The text string to be converted.
        names
            Parser names to be used. If not specified. all of the registered
            parsers will be used.

        Returns
        -------
        converted source text.
        """
        with codecs.open(path, "r", "utf8") as file:
            source = file.read()
        source = source.replace("\r\n", "\n").replace("\r", "\n")
        return self.convert(source, names)

    def __call__(self, *names: str) -> Callable[[str], str]:
        return partial(self.convert_from_file, names=names)


def resolve_renderer(name: str) -> Renderer:
    name = name[0].upper() + name[1:]
    module = importlib.import_module("pheasant")
    if hasattr(module, name):
        Renderer_ = getattr(module, name)
        if issubclass(Renderer_, Renderer):
            return Renderer_()
    raise ImportError(f"Renderer '{name}' not found.")

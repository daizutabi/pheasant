import importlib
from typing import Dict, List, Optional, Union

from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer


class Converter:
    def __init__(self):
        self.parsers: Dict[str, Parser] = {}
        self.renderers: Dict[str, List[Renderer]] = {}
        self.names: List[str] = []

    def register(self, name: str, renderers: List[Union[Renderer, str]]):
        """Register renderer's processes

        Parameters
        ----------
        name
            The name of Parser
        renderers
            List of Renderer's instance or name of Renderer
        """
        if name in self.parsers:
            raise ValueError
        self.names.append(name)
        parser = Parser()
        self.parsers[name] = parser
        self.renderers[name] = [
            resolve_renderer(renderer) if isinstance(renderer, str) else renderer
            for renderer in renderers
        ]
        for renderers_ in self.renderers.values():
            for renderer in renderers_:
                for pattern, render in renderer.renders.items():
                    parser.register(pattern, render)

    def convert(self, source: str, names: Optional[List[str]] = None) -> str:
        names = names or self.names
        for name in names:
            parser = self.parsers[name]
            source = "".join(parser.parse(source))

        return source


def resolve_renderer(name: str) -> Renderer:
    name = name[0].upper() + name[1:]
    module = importlib.import_module("pheasant")
    if hasattr(module, name):
        Renderer_ = getattr(module, name)
        if issubclass(Renderer_, Renderer):
            return Renderer_()
    raise ImportError(f"Renderer '{name}' not found.")

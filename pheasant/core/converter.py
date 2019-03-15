from typing import Dict, List, Optional, Tuple

from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer


class Converter:
    def __init__(self):
        self.parsers: Dict[str, Parser] = {}
        self.renderers: Dict[str, Tuple[Renderer]] = {}
        self.names: List[str] = []

    def register(self, name: str, renderers: Tuple[Renderer]):
        """Register renderer's processes

        Parameters
        ----------
        name
            The name of Parser
        renderers
            List of Renderer
        """
        if name in self.parsers:
            raise ValueError
        self.names.append(name)
        parser = Parser(name)
        self.parsers[name] = parser
        self.renderers[name] = renderers
        for renderer in renderers:
            for pattern, render in renderer.renders.items():
                parser.register(pattern, render)

    def convert(self, source: str, names: Optional[List[str]] = None) -> str:
        names = names or self.names
        for name in names:
            parser = self.parsers[name]
            source = "".join(parser.parse(source))
        return source

from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Number


class Converter:
    def __init__(self):
        self.parser = Parser()

    def register(self, *renderers: Renderer):
        for renderer in renderers:
            for pattern, render in renderer.renders.items():
                self.parser.register(pattern, render)

    def convert(self, source: str) -> str:
        return "".join(self.parser.parse(source))


converter = Converter()
converter.convert('abc')
jupyter = Jupyter()
number = Number()
converter.register(jupyter, number)

from pheasant.core.parser import Parser
from pheasant.core.renderer import Renderer


class Converter:
    def __init__(self):
        self.parser = Parser()

    def register(self, renderer: Renderer):
        for pattern, render in renderer.renders.items():
            self.parser.register(pattern, render)

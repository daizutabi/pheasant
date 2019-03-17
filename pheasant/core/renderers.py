import importlib
from collections import OrderedDict
from typing import Dict, Iterable, List, Type, Union

from pheasant.core.renderer import Renderer


class Renderers:
    renderer_types: Dict[str, Type[Renderer]]

    def __init__(self):
        self.update_renderer_types()
        self.renderers: OrderedDict[str, List[Renderer]] = OrderedDict()

    def register(
        self,
        name: str,
        renderers: Union[Union[Renderer, str], Iterable[Union[Renderer, str]]],
    ):
        """
        Parameters
        ----------
        name
            The name of Renderers
        renderers
            List of Renderer's instance
        """
        if not isinstance(renderers, Iterable) or isinstance(renderers, str):
            renderers = [renderers]

        def to_renderer(renderer: Union[Renderer, str]) -> Renderer:
            if isinstance(renderer, str):
                return Renderers.renderer_types[renderer]()
            else:
                return renderer

        self.renderers[name] = [to_renderer(renderer) for renderer in renderers]

    def __getitem__(self, item) -> Union[List[Renderer], Renderer]:
        if isinstance(item, str):
            return self.renderers[item]
        elif isinstance(item, tuple):
            renderers = self.renderers[item[0]]
            if isinstance(item[1], int):
                return renderers[item[1]]
            else:
                for renderer in renderers:
                    if renderer.name == item[1]:
                        return renderer
                else:
                    raise KeyError
        raise IndexError

    def __iter__(self) -> Iterable[Renderer]:
        return (
            renderer for renderers in self.renderers.values() for renderer in renderers
        )

    def items(self):
        return self.renderers.items()

    def keys(self):
        return self.renderers.keys()

    def values(self):
        return self.renderers.values()

    @classmethod
    def update_renderer_types(cls):
        module = importlib.import_module("pheasant")
        cls.renderer_types = {
            name.lower(): getattr(module, name)
            for name in module.__dict__["__all__"]  # for mypy
            if issubclass(getattr(module, name), Renderer)
        }

from collections import OrderedDict
from dataclasses import field
from typing import Dict, Iterable, Iterator, List, Union

from pheasant.core.base import Base
from pheasant.core.renderer import Renderer


class Renderers(Base):
    renderers: Dict[str, List[Renderer]] = field(default_factory=OrderedDict)

    def __post_repr__(self):
        return len(self)

    def register(self, name: str, renderers: Iterable[Renderer]):
        """
        Parameters
        ----------
        name
            The name of Renderers
        renderers
            List of Renderer's instance
        """
        self.renderers[name] = list(renderers)

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

    def __len__(self):
        return len(list(iter(self)))

    def __iter__(self) -> Iterator[Renderer]:
        return (
            renderer for renderers in self.renderers.values() for renderer in renderers
        )

    def items(self):
        return self.renderers.items()

    def keys(self):
        return self.renderers.keys()

    def values(self):
        return self.renderers.values()

from dataclasses import field
from typing import Any, Callable, Dict, Optional

from pheasant.core.base import Base, get_render_name


class Decorator(Base):
    decorates: Dict[str, Callable[..., None]] = field(default_factory=dict)

    def register(self, renderer, decorate: Callable[..., None]):
        for render in renderer.renders.values():
            render_name = get_render_name(render)
            self.decorates[render_name] = decorate

    def decorate(self, cell):
        if cell.match is None and None in self.decorates:
            self.decorates[None](cell)
        elif cell.match is not None and cell.render_name in self.decorates:
            self.decorates[cell.render_name](cell)

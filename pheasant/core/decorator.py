import functools
import re
from dataclasses import field
from typing import Callable, Dict, Union

from pheasant.core.base import Base, get_render_name

SURROUND_TAG = re.compile(
    r"^([^<]*)<(?P<tag>(span|div))(.*)</(?P=tag)>([^>]*)$", re.DOTALL
)


class Decorator(Base):
    decorates: Dict[str, Callable[..., None]] = field(default_factory=dict)
    class_names: Dict[str, str] = field(default_factory=dict)

    def register(self, decorate: Union[Callable, str], renderers):
        if isinstance(decorate, str):
            decorate = getattr(self, decorate)
        if not isinstance(renderers, list):
            renderers = [renderers]
        for renderer in renderers:
            for render in renderer.renders.values():
                render_name = get_render_name(render)
                self.decorates[render_name] = decorate  # type: ignore
                self.class_names[render_name] = self.class_name(render_name)

    def class_name(self, render_name):
        return self.name + "-" + render_name.split("__")[-1].replace("_", "-")

    def decorate(self, cell):
        if cell.match is None and None in self.decorates:
            self.decorates[None](cell)
        elif cell.match is not None and cell.render_name in self.decorates:
            self.decorates[cell.render_name](cell)

    def surround(self, cell):
        class_name = self.class_names[cell.render_name]
        replace = r'\1<\2 class="{class_name}"><\2\4</\2></\2>\5'
        replace = replace.format(class_name=class_name)
        cell.output = SURROUND_TAG.sub(replace, cell.output)


def comment(name):
    def deco(render):
        @functools.wraps(render)
        def render_(self, context, splitter, parser):
            if context[name].startswith("#"):
                yield context["_source"].replace(context[name], context[name][1:])
            else:
                yield from render(self, context, splitter, parser)

        return render_

    return deco

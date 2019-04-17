import datetime
import functools
import re
from dataclasses import field
from typing import Callable, Dict, Iterable, Union

from pheasant.core.base import Base
from pheasant.renderers.jupyter.client import execution_report
from pheasant.utils.time import format_timedelta_human

SURROUND_TAG = re.compile(
    r"^([^<]*)<(?P<tag>(span|div))(.*)</(?P=tag)>([^>]*)$", re.DOTALL
)


class Decorator(Base):
    decorates: Dict[str, Callable[..., None]] = field(default_factory=dict)
    class_names: Dict[str, str] = field(default_factory=dict)

    def register(self, renderers: Iterable, decorate: Union[Callable, str]):
        if isinstance(decorate, str):
            decorate = getattr(self, decorate)
        for renderer in renderers:
            if renderer.parser:
                renderer.parser.decorator = self  # type: ignore
            for render_name, render in renderer.renders.items():
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
        if cell.output:
            class_name = self.class_names[cell.render_name]
            cell.output = surround(cell.output, class_name)


def surround(source, class_name):
    """Surround a html source with a tag accoring to the most out-side tag."""
    replace = r'\1<\2 class="{class_name}"><\2\4</\2></\2>\5'
    replace = replace.format(class_name=class_name)
    return SURROUND_TAG.sub(replace, source)


def commentable(name):
    def deco(render):
        @functools.wraps(render)
        def render_(self, context, splitter, parser):
            if context[name].startswith("#"):
                yield context["_source"].replace(context[name], context[name][1:])
            else:
                yield from render(self, context, splitter, parser)

        return render_

    return deco


def monitor(format=True):
    def deco(func):
        @functools.wraps(func)
        def func_(*args, **kwargs):
            start_kernel = execution_report["life"]
            start_func = datetime.datetime.now()
            output = func(*args, **kwargs)
            end_func = datetime.datetime.now()
            end_kernel = execution_report["life"]

            timedelta = end_func - start_func
            if format:
                timedelta = format_timedelta_human(timedelta)
            func_.func_time = timedelta

            timedelta = end_kernel - start_kernel
            if format:
                timedelta = format_timedelta_human(timedelta)
            func_.kernel_time = timedelta
            return output

        return func_

    return deco

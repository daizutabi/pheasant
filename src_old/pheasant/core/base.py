import re
from dataclasses import dataclass, field, make_dataclass
from typing import Any, Callable, Dict, Generator, Iterator, Match, Optional

Splitter = Generator[Any, Optional[str], None]
Render = Callable[..., Iterator[str]]


class MetaClass(type):
    def __new__(cls, name, bases, dict):
        decorator = dataclass(repr=False, eq=False)
        return decorator(type.__new__(cls, name, bases, dict))


class Base(metaclass=MetaClass):
    name: str = ""
    config: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.name = self.name or self.__class__.__name__.lower()

    def __repr__(self):
        post = self.__post_repr__()
        post = f"[{post}]" if post else ""
        return f"<{self.__class__.__name__}#{self.name}{post}>"

    def __post_repr__(self):
        return ""

    def _update(self, name: str, update: Dict[str, Any]) -> None:
        arg = getattr(self, name)
        for key, value in update.items():
            if key not in arg:
                arg[key] = value
            elif isinstance(value, list):
                arg[key].extend(value)
            elif isinstance(value, dict):
                arg[key].update(value)
            else:
                arg[key] = value


def get_render_name(render: Render) -> str:
    """Return a render name which is used to resolve the matched pattern.

    Usualy, render_name = '<class_name>__<render_function_name>' in lower case.
    If render function name starts with 'render_', it is omitted from the name.

    Parameters
    ----------
    render
        Render function.

    Returns
    -------
    str
        Name of the render.
    """

    def iterate(render):
        if hasattr(render, "__self__"):
            renderer = render.__self__
            name = renderer.__class__.__name__.lower()
            yield name
            if hasattr(renderer, "name") and renderer.name != name:
                yield renderer.name
        name = render.__name__
        if name.startswith("render_"):
            yield name[7:]
        else:
            yield name

    return "__".join(iterate(render))


def rename_pattern(pattern: str, render_name: str) -> str:
    """Rename a pattern with a render name to determine the corresponding render.

    Triple underscores divides the pattern name into a render name to determine a
    render and a real name for a render processing.
    """
    name_pattern = r"\(\?P<(.+?)>(.+?)\)"
    replace = f"(?P<{render_name}___\\1>\\2)"
    pattern = re.sub(name_pattern, replace, pattern)
    name_pattern = r"\(\?P=(.+?)\)"
    replace = f"(?P={render_name}___\\1)"
    pattern = re.sub(name_pattern, replace, pattern)
    pattern = f"(?P<{render_name}>{pattern})"
    return pattern


@dataclass(eq=False)
class Cell:
    source: str
    match: Optional[Match]
    output: str

    def _render(self):  # for check the render function in rederer. See Script class.
        pass


def make_cell_class(pattern: str, render: Render, render_name: str) -> type:
    fields = [
        ("context", Dict[str, str]),
        ("pattern", str, field(default=pattern, init=False)),
        ("render_name", str, field(default=render_name, init=False)),
    ]

    def _render(self, splitter, parser):
        yield from render(self.context, splitter, parser)

    def parse(self, splitter, parser):
        return "".join(self.render(splitter, parser))

    return make_dataclass(
        "Cell",
        fields,  # type: ignore
        namespace={"render": _render, "parse": parse, "_render": render},
        bases=(Cell,),
    )

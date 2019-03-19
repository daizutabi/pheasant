import re
from dataclasses import dataclass, field, make_dataclass
from typing import (Any, Callable, Dict, Generator, Iterable, Iterator, List,
                    Match, Optional, Pattern, Tuple)

from pheasant.core.base import Base

Splitter = Generator[Any, Optional[str], None]
Render = Callable[..., Iterator[str]]


@dataclass(eq=False)
class Cell:
    source: Optional[str]
    match: Optional[Match]


class Parser(Base):
    patterns: Dict[str, str] = field(default_factory=dict)
    renders: Dict[str, Render] = field(default_factory=dict)
    pattern: Optional[Pattern] = None
    cell_classes: Dict[str, type] = field(default_factory=dict)

    def __post_repr__(self):
        return len(self.patterns)

    def register(self, pattern: str, render: Render, render_name: str = "") -> type:
        if not render_name:
            render_name = get_render_name(render)
        cell_class = make_cell_class(pattern, render, render_name)
        self.cell_classes[render_name] = cell_class
        pattern = rename_pattern(pattern, render_name)
        self.patterns[render_name] = pattern
        self.renders[render_name] = render
        return cell_class

    def parse(self, source: str) -> Iterator[str]:
        splitter = self.split(source)
        next(splitter)
        for cell in splitter:
            if cell.match:
                yield from cell.render(
                    context=cell.context, splitter=splitter, parser=self
                )  # Deligates to render
            else:
                yield cell.source

    def split(self, source: str) -> Splitter:
        """Split the source into a cell and yield it."""
        if not self.patterns:
            raise ValueError("No pattern registered")
        elif self.pattern is None:
            self.pattern = re.compile(
                "|".join(self.patterns.values()), re.MULTILINE | re.DOTALL
            )

        def get(cell, attr=None):
            if attr is None:
                return cell
            else:
                return getattr(cell, attr)

        cursor = 0
        attr = yield
        for match in self.pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                attr = yield get(Cell(source[cursor:start], None), attr)
            attr = yield get(self.resolve(match), attr)
            cursor = end
        if cursor < len(source):
            yield get(Cell(source[cursor:], None), attr)

    def resolve(self, match: Match[str]) -> Any:  # Acually, Any is Cell-based instance.
        """Resolve a Match object and return a dataclass instance called `cell`.

        Returned cell contains the required and helpful information for
        rendering the match object such as render's name, render function,
        the groups of the match object as a context, etc.

        Parameters
        ----------
        match
            A match object.

        Returns
        -------
        cell : dataclass instance
        """
        groupdict = match.groupdict()
        render_name = ""

        def rename_for_render(key):
            nonlocal render_name
            if "___" in key:
                return key.split("___")[-1]
            else:
                render_name = key
                return "_source"

        context = {
            rename_for_render(key): value
            for key, value in groupdict.items()
            if value is not None
        }

        return self.cell_classes[render_name](None, match, context)


def get_render_name(render: Render) -> str:
    """Return a render name which is used to resolve the mattched pattern.
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
    """Rename a pattern with a render name to enable to determine the render which
    should process the pattern. Triple underscores divides the pattern name into
    a render name to determine a render and a real name for a render processing.
    """
    name_pattern = r"\(\?P<(.+?)>(.+?)\)"
    replace = f"(?P<{render_name}___\\1>\\2)"
    pattern = re.sub(name_pattern, replace, pattern)
    name_pattern = r"\(\?P=(.+?)\)"
    replace = f"(?P={render_name}___\\1)"
    pattern = re.sub(name_pattern, replace, pattern)
    pattern = f"(?P<{render_name}>{pattern})"
    return pattern


def make_cell_class(pattern: str, render: Render, render_name: str) -> type:
    fields = [
        ("context", Dict[str, str]),
        ("pattern", str, field(default=pattern, init=False)),
        ("render", Callable[..., Generator], field(default=render)),  # NG: init=False
        ("render_name", str, field(default=render_name, init=False)),
    ]
    return make_dataclass("Cell", fields, bases=(Cell,))  # type: ignore

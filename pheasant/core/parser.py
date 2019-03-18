import re
from dataclasses import dataclass, field, make_dataclass
from typing import Any, Callable, Dict, Iterator, Match, Optional, Pattern

from pheasant.core.base import Base

Render = Callable[[Any, "Parser"], Iterator[str]]


@dataclass(eq=False)
class Cell:
    source: str
    match: Optional[Match] = None


class Parser(Base):
    patterns: Dict[str, str] = field(default_factory=dict)
    renders: Dict[str, Render] = field(default_factory=dict)
    pattern: Optional[Pattern] = None
    context_classes: Dict[str, type] = field(default_factory=dict)
    cell_classes: Dict[str, type] = field(default_factory=dict)

    def __post_repr__(self):
        return len(self.patterns)

    def register(self, pattern: str, render: Render, postfix: str = "") -> type:
        name = render_name(render, postfix)
        context_class = make_context_class(pattern, name)
        self.context_classes[name] = context_class
        cell_class = make_cell_class(context_class, name, render)
        self.cell_classes[name] = cell_class
        pattern = rename_pattern(pattern, name)
        self.patterns[name] = pattern
        self.renders[name] = render
        return context_class

    def parse(self, source: str) -> Iterator[str]:
        self.splitter = self.split(source)
        for cell in self.splitter:
            if cell.match:
                yield cell.convert()  # Deligates to render
                # yield from cell.render(cell.context, self)
            else:
                yield cell.source

    def __iter__(self):
        return self

    def __next__(self):
        if self.splitter:
            return next(self.splitter)
        else:
            raise StopIteration

    def split(self, source: str) -> Iterator[Any]:
        """Split the source into a cell and yield it

        The type of the cell depends on the sent arg `type_`.
        """
        if not self.patterns:
            yield Cell(source)
            return

        if self.pattern is None:
            self.pattern = re.compile(
                "|".join(self.patterns.values()), re.MULTILINE | re.DOTALL
            )

        cursor = 0
        for match in self.pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                yield Cell(source[cursor:start])
            yield self.resolve(match)
            cursor = end
        if cursor < len(source):
            yield Cell(source[cursor:])

    def resolve(self, match: Match[str]) -> Any:
        """Resolve a Match object and return a dictionary.

        Returned dictionary contains the required and helpful information for
        rendering the match object such as pattern's name, render function,
        the groups of the match object as a context, etc.

        Parameters
        ----------
        match
            A match object.

        Returns
        -------
        cell
        """
        groupdict = match.groupdict()
        name = ""

        def rename_for_render(key):
            nonlocal name
            if "___" in key:
                return key.split("___")[-1]
            else:
                name = key
                return "_source"

        context = {
            rename_for_render(key): value
            for key, value in groupdict.items()
            if value is not None
        }
        context = self.context_classes[name](**context)
        render = self.renders[name]

        def convert() -> str:
            return "".join(render(context, self))

        return self.cell_classes[name](
            source=match.group(),
            match=match,
            render_name=name,  # not required, already set
            context=context,
            render=render,  # not required, already set
            convert=convert,
        )


def rename_pattern(pattern: str, name: str) -> str:
    """Rename a pattern with a prefix to enable to determine the render which
    should process the pattern. Double underscore divides the pattern name into
    a render name to determine a render and a real name for a render's processing.
    """
    name_pattern = r"\(\?P<(.+?)>(.+?)\)"
    replace = f"(?P<{name}___\\1>\\2)"
    pattern = re.sub(name_pattern, replace, pattern)
    name_pattern = r"\(\?P=(.+?)\)"
    replace = f"(?P={name}___\\1)"
    pattern = re.sub(name_pattern, replace, pattern)
    pattern = f"(?P<{name}>{pattern})"
    return pattern


def render_name(render: Render, postfix: str = "") -> str:
    """Return a suitable render name as a pattern name.

    Parameters
    ----------
    obj
        Named object for a pattern.

    Returns
    -------
    str
        The suitable object name as a pattern name.
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
        if postfix:
            yield postfix

    return "__".join(iterate(render))


def make_context_class(pattern: str, name: str) -> type:
    name_pattern = r"\(\?P<(.+?)>.+?\)"
    fields = [
        (name, str, field(default="")) for name in re.findall(name_pattern, pattern)
    ]
    extra_fields = [
        ("_render_name", str, field(default=name)),
        ("_source", str, field(default="")),
    ]
    return make_dataclass("Context", fields + extra_fields)  # type: ignore


def make_cell_class(context_class: type, name: str, render: Render) -> type:
    fields = [
        ("render_name", str, field(default=name)),
        ("context", context_class, field(default_factory=context_class)),
        (
            "render",
            Callable[[context_class, Parser], Iterator[str]],
            field(default=render),
        ),
        ("convert", Optional[Callable[[], str]], field(default=None)),
    ]
    return make_dataclass("Cell", fields, bases=(Cell,))  # type: ignore

import re
from dataclasses import dataclass, field, make_dataclass
from typing import Any, Callable, Dict, Iterator, Match, Optional, Pattern

from pheasant.core.base import Base

Render = Callable[[Any], Iterator[str]]  # Any = Context dataclass


@dataclass(eq=False)
class Context:
    source: Optional[str]
    match: Optional[Match]


class Parser(Base):
    patterns: Dict[str, str] = field(default_factory=dict)
    renders: Dict[str, Render] = field(default_factory=dict)
    pattern: Optional[Pattern] = None
    group_classes: Dict[str, type] = field(default_factory=dict)
    context_classes: Dict[str, type] = field(default_factory=dict)

    def __post_repr__(self):
        return len(self.patterns)

    def register(self, pattern: str, render: Render, postfix: str = "") -> type:
        group_class = make_group_class(pattern)
        render_name = get_render_name(render, postfix)
        self.group_classes[render_name] = group_class
        context_class = make_context_class(group_class, render_name, render, self)
        self.context_classes[render_name] = context_class
        pattern = rename_pattern(pattern, render_name)
        self.patterns[render_name] = pattern
        self.renders[render_name] = render
        return context_class

    def parse(self, source: str) -> Iterator[str]:
        splitter = self.split(source)
        for context in splitter:
            if context.match:
                context.splitter = splitter
                yield from context.render(context)  # Deligates to render
            else:
                yield context.source

    def split(self, source: str) -> Iterator[Any]:
        """Split the source into a cell and yield it."""
        if not self.patterns:
            yield Context(source, None)
            return

        if self.pattern is None:
            self.pattern = re.compile(
                "|".join(self.patterns.values()), re.MULTILINE | re.DOTALL
            )

        cursor = 0
        for match in self.pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                yield Context(source[cursor:start], None)
            yield self.resolve(match)
            cursor = end
        if cursor < len(source):
            yield Context(source[cursor:], None)

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

        group = {
            rename_for_render(key): value
            for key, value in groupdict.items()
            if value is not None
        }
        # IMPORTANT: To make `_source` at once is required to set `render_name`.
        del group["_source"]
        group = self.group_classes[render_name](**group)

        return self.context_classes[render_name](None, match, group, None)


def get_render_name(render: Render, postfix: str = "") -> str:
    """Return a render name which is used to resolve the mattched pattern.
    Usualy, render_name = '<class_name>__<render_function_name>' in lower case.
    If render function name starts with 'render_', it is omitted from the name.

    Parameters
    ----------
    render
        Render function.
    postfix
        Additional postfix.

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
        if postfix:
            yield postfix

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


def make_group_class(pattern: str) -> type:
    name_pattern = r"\(\?P<(.+?)>.+?\)"
    fields = [
        (name, str, field(default="")) for name in re.findall(name_pattern, pattern)
    ]
    return make_dataclass("Group", fields)  # type: ignore


def make_context_class(
    group_class: type, render_name: str, render: Render, parser: Parser
) -> type:
    fields = [
        ("group", group_class),
        ("splitter", Optional[Iterator[str]]),
        ("render_name", str, field(default=render_name)),
        ("render", Callable[[Any], Iterator[str]], field(default=render)),
        ("parser", Parser, field(default=parser)),
    ]
    return make_dataclass("Cell", fields, bases=(Context,))  # type: ignore

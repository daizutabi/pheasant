import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, Match, Optional, Pattern

from pheasant.core.base import Base

Render = Callable[[Dict[str, str], "Parser"], Iterator[str]]


@dataclass(eq=False)
class Cell:
    source: str
    match: Optional[Match] = None
    name: Optional[str] = None
    context: Dict[str, str] = field(default_factory=dict)
    render: Optional[Render] = None
    result: Optional[Callable[[], str]] = None


@dataclass(repr=False)
class Parser(Base):
    patterns: Dict[str, str] = field(default_factory=dict)
    renders: Dict[str, Render] = field(default_factory=dict)
    pattern: Optional[Pattern] = None

    def __post_repr__(self):
        return len(self.patterns)

    def register(self, pattern: str, render: Render) -> None:
        name = object_name(render)
        pattern = rename_pattern(pattern, name)
        self.patterns[name] = f"(?P<{name}>{pattern})"
        self.renders[name] = render

    def parse(self, source: str) -> Iterator[str]:
        self.splitter = self.split(source)
        for cell in self.splitter:
            if cell.render:
                yield from cell.render(cell.context, self)  # Deligates to render
            else:
                yield cell.source

    def __next__(self):
        if self.splitter:
            return next(self.splitter)
        else:
            raise StopIteration

    def split(self, source: str) -> Iterator[Cell]:
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

    def resolve(self, match: Match[str]) -> Cell:
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
            if "__" in key:
                return key.split("__")[1]
            else:
                name = key
                return "_source"

        context = {
            rename_for_render(key): value
            for key, value in groupdict.items()
            if value is not None
        }
        assert match.group() == context["_source"]  # Just for debug. Delete later!
        render = self.renders[name]

        def result() -> str:
            return "".join(render(context, self))

        return Cell(
            source=match.group(),
            match=match,
            name=name,
            context=context,
            render=render,
            result=result,
        )


def rename_pattern(pattern: str, name: str) -> str:
    """Rename a pattern with a prefix to enable to determine the render which
    should process the pattern. Double underscore divides the pattern name into
    a render name to determine a render and a real name for a render's processing.

    Examples
    --------
    >>> rename_pattern(r"(?P<name>A.*?Z)(?P=name)", "abc")
    '(?P<abc__name>A.*?Z)(?P=abc__name)'
    """
    name_pattern = r"\(\?P<(.+?)>(.+?)\)"
    replace = f"(?P<{name}__\\1>\\2)"
    pattern = re.sub(name_pattern, replace, pattern)
    name_pattern = r"\(\?P=(.+?)\)"
    replace = f"(?P={name}__\\1)"
    pattern = re.sub(name_pattern, replace, pattern)
    return pattern


def object_name(obj: Any) -> str:
    """Return a suitable object name as a pattern name.

    Parameters
    ----------
    obj
        Named object for a pattern.

    Returns
    -------
    str
        The suitable object name as a pattern name.

    Examples
    --------
    >>> class A:
    ...   def func(self):
    ...      passs
    >>> a = A()
    >>> object_name(a.func)
    'A_func'
    >>> def func():
    ...   pass
    >>> object_name(func).startswith('func_0x')
    True
    """
    name = str(obj)
    if "method" in str(type(obj)):
        return str(obj).split(" ")[2].replace(".", "_")
    elif "." in name:
        names = name.split(".")[-1].split(" ")
        if "function" in str(type(obj)):
            return "_".join([names[0], names[2][:-1]])
        else:
            raise TypeError(f"Unknown type: {obj}")
    else:
        names = name.split(" ")
        return "_".join([names[1], names[3][:-1]])

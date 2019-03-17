import re
from dataclasses import dataclass, field
from typing import (Any, Callable, Dict, Generator, Iterator, Match, Optional,
                    Pattern, Union)

from pheasant.core.base import Base

Render = Callable[[Dict[str, str], "Parser"], Iterator[str]]
Cell = Union[str, Dict[str, Any], Match[str]]
Splitter = Generator[Optional[Cell], Optional[type], None]
Seed = Dict[str, Any]


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
        self.generator = self.splitter(source)
        next(self.generator)  # go to the first yield.
        for cell in self.generator:
            if isinstance(cell, str):
                yield cell
            elif isinstance(cell, Match):
                seed = self.sow(cell)
                yield from seed["render"](seed["context"], self)  # Deligates to render

    def send(self, arg):
        """Shortcut to self.generator.send"""
        if self.generator:
            return self.generator.send(arg)
        else:
            return None

    def splitter(self, source: str) -> Splitter:
        """Split the source into a cell and yield it

        The type of the cell depends on the sent arg `type_`.
        """
        type_ = yield None
        if not self.patterns:
            yield source
            return
        if self.pattern is None:
            self.pattern = re.compile(
                "|".join(self.patterns.values()), re.MULTILINE | re.DOTALL
            )
        cursor = 0
        for match in self.pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                plain = source[cursor:start]
                type_ = yield self.reap(plain, None, type_)
            type_ = yield self.reap(match.group(), match, type_)
            cursor = end
        if cursor < len(source):
            plain = source[cursor:]
            yield self.reap(plain, None, type_)

    def reap(
        self, source: str, match: Optional[Match[str]], type_: Optional[type]
    ) -> Cell:
        """Reap a plain source or `Match` object according to what the client
        wants to be sent.

        Parameters
        ----------
        source
            Plain soure or matched source. If `match` is None, `source` is a string
            which is not matched by any patterns registered.
        match
            Match object.
        type_
            str for a plain text source, dict for a dictionary which contains
            contents for rendering, and None for a plain text source or
            a Match object according to whether current source matches any
            patterns or not.

        Returns
        -------
        str, dict, or Match
            Return type depends on the `type_` arg that was sent from a client.
        """
        if type_ == str:
            return source
        elif type_ == dict:
            if match:
                return dict(match=match, **self.sow(match))
            else:
                return dict(
                    name=None, render=None, source=source, context={}, match=None
                )
        else:
            return match or source

    def sow(self, match: Match[str]) -> Seed:
        """Sow a `seed` (render or other information) suitable for the match object
        according to the pattern name.

        Return a dictionary which contains the required and helpful information for
        rendering the match object such as pattern's name, render, context, etc.

        Parameters
        ----------
        match
            A match object.

        Returns
        -------
        dict
        """
        groupdict = match.groupdict()
        name = ""

        def rename_for_render(key):
            nonlocal name
            if "__" in key:
                return key.split("__")[1]
            else:
                name = key
                return "__group__"

        context = {
            rename_for_render(key): value
            for key, value in groupdict.items()
            if value is not None
        }
        source = context.pop("__group__")
        context["_source"] = source
        render = self.renders[name]

        def result() -> str:
            return "".join(render(context, self))

        return dict(
            name=name, render=render, result=result, source=source, context=context
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

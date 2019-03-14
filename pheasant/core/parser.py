import re
from typing import (Any, Callable, Dict, Generator, Iterable, Match, Optional,
                    Pattern, Union)

Splitted = Union[str, Dict[str, Any], Match[str]]
Splitter = Generator[Splitted, Any, None]
Render = Callable[[Dict[str, str], "Parser"], Iterable[str]]
Gen = Generator[Any, Optional[type], None]


class Parser:
    def __init__(self):
        self.patterns: Dict[str, str] = {}
        self.renders: Dict[str, Render] = {}
        self.pattern: Optional[Pattern] = None
        self.generator: Optional[Gen] = None

    def register(self, pattern: str, render: Render) -> None:
        name = object_name(render)
        pattern = rename_pattern(pattern, name)
        self.patterns[name] = f"(?P<{name}>{pattern})"
        self.renders[name] = render

    def parse(self, source: str) -> Iterable[str]:
        self.generator = self.splitter(source)
        next(self.generator)
        for splitted in self.generator:
            if isinstance(splitted, str):
                yield splitted
            elif isinstance(splitted, Match):
                cell = self._reap(splitted)
                yield from cell["render"](cell["context"], self)

    def send(self, arg):
        return self.generator.send(arg)

    def splitter(self, source: str) -> Gen:
        self.pattern = re.compile(
            "|".join(self.patterns.values()), re.MULTILINE | re.DOTALL
        )
        cursor = 0
        type_ = yield None
        for match in self.pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                type_ = yield self._sow(source[cursor:start], None, type_)
            type_ = yield self._sow(match.group(), match, type_)
            cursor = end
        if cursor < len(source):
            yield self._sow(source[cursor:], None, type_)

    def _sow(
        self, source: str, match: Optional[Match[str]], type_: Optional[type]
    ) -> Splitted:
        if type_ == str:
            return source
        elif type_ == dict:
            if match:
                return self._reap(match)
            else:
                return dict(name=None, render=None, source=source, context={})
        elif type_ == all:
            if match:
                return dict(match=match, **self._reap(match))
            else:
                return dict(
                    name=None, render=None, source=source, context={}, match=None
                )
        else:
            return match or source

    def _reap(self, match: Match[str]) -> Dict[str, Any]:
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
        render = self.renders[name]

        def result() -> str:
            return "".join(render(context, self))

        return dict(
            name=name, render=render, result=result, source=source, context=context
        )


def rename_pattern(pattern: str, name: str) -> str:
    """Rename with prefix.

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

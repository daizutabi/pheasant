import importlib
from typing import (Any, Callable, Dict, Iterable, List, Match, Optional,
                    Pattern, Tuple)

History = Optional[Tuple[str, ...]]
Cell = Tuple[str, History]
Call = Callable[[Match, Optional[History]], str]
Rule = Tuple[Pattern, Optional[Call]]


class Converter:
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config: Dict[str, Any] = config or {}
        try:
            module = importlib.import_module(f"pheasant.{name}.config")
            if hasattr(module, "config"):
                self.config.update(module.config)  # type: ignore
        except ModuleNotFoundError:
            pass

        self.keys: List[str] = []
        self.patterns: List[Pattern] = []
        self.calls: List[Call] = []

    def register(self, key: str, pattern: Pattern, call: Call) -> None:
        self.keys.append(key)
        self.patterns.append(pattern)
        self.calls.append(call)

    def convert(self, source: str):
        return "".join(self.render(source))

    def render(self, source: str) -> Iterable[str]:
        for source, history in self.parse(source):
            yield source

    def parse(
        self, source: str, index: int = 0, history: History = None
    ) -> Iterable[Cell]:
        if index == len(self.patterns):
            yield source, history
            return

        pattern = self.patterns[index]
        call = self.calls[index]
        if history:
            history_match = history + (self.keys[index],)
        else:
            history_match = (self.keys[index],)
        cursor = 0
        index += 1
        for match in pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                yield from self.parse(source[cursor:start], index, history)
            converted = call(match, history) if call else match.group()
            yield from self.parse(converted, index, history_match)
            cursor = end
        if cursor < len(source):
            yield from self.parse(source[cursor:], index, history)

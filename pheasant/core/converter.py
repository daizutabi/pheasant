import importlib
import logging
import re
import typing
from typing import Any, Callable, Dict, Iterable, List, Match, Optional

from pheasant.utils import read_source

logger = logging.getLogger("mkdocs")
Call = Callable[[Dict[str, str]], Iterable[str]]


class Renderer:
    flags = re.MULTILINE | re.DOTALL

    def __init__(self):
        self.patterns: List[str] = []
        self.calls: Dict[str, Call] = {}
        self.pattern: Optional[typing.Pattern] = None

    def register(self, name: str, pattern: str, call: Call) -> None:
        self.patterns.append(f"(?P<{name}>{pattern})")
        self.calls[name] = call

    def compile(self) -> typing.Pattern:
        pattern = "|".join(self.patterns)
        self.pattern = re.compile(pattern, self.flags)
        return self.pattern

    def parse(self, source: str) -> Iterable[str]:
        if self.pattern is None:
            pattern = self.compile()
        else:
            pattern = self.pattern

        cursor = 0
        for match in pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                yield source[cursor:start]
            yield from self.render(match)
            cursor = end
        if cursor < len(source):
            yield source[cursor:]

    def render(self, match: Match) -> Iterable[str]:
        groupdict = match.groupdict()
        for key, value in groupdict.items():
            if value and len(key.split("__")) == 2:
                break
        pre = key + "__"
        context = {
            key_.replace(pre, ""): value
            for key_, value in groupdict.items()
            if key_.startswith(pre)
        }

        yield from self.calls[key](context)


class Converter:
    renderer = Renderer()

    def __init__(self):
        self.clients: Dict[str, Client] = {}

    def client(self, name: str) -> "Client":
        if name not in self.clients:
            client = Client(name)
            client.renderer = self.renderer
            self.clients[name] = client
        return self.clients[name]

    def convert(self, source: str):
        return "".join(self.renderer.parse(source))


converter = Converter()


class Client:
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        module_str = self.__module__.replace(".client", ".config")
        module = importlib.import_module(module_str)
        if hasattr(module, "config"):
            default_config = getattr(module, "config")
        else:
            default_config = {}
        if config:
            for key, value in config.items():
                if key not in default_config:
                    default_config[key] = value
                elif isinstance(default_config[key], list):
                    default_config[key].extend(config[key])
                elif isinstance(default_config[key], dict):
                    default_config[key].update(config[key])
        self.config = default_config
        self.converter = converter
        self.renderer = converter.renderer

    def register(self, name: str, pattern: str, call: Call) -> None:
        if self.renderer:
            name_pattern = r"\(\?P<(.+?)>(.+?)\)"
            replace = f"(?P<{self.name}__{name}__\\1>\\2)"
            pattern = re.sub(name_pattern, replace, pattern)
            name_pattern = r"\(\?P=(.+?)\)"
            replace = f"(?P={self.name}__{name}__\\1)"
            pattern = re.sub(name_pattern, replace, pattern)
            self.renderer.register(f"{self.name}__{name}", pattern, call)


def convert(source: str) -> str:
    """Convert the source file.

    This function is the starting point of conversion.
    From this function, each convert function of clients is called.
    Then finally the results are returned to the plugin for further
    processing.
    """
    from pheasant.core.config import config as pheasant_config

    logger.debug("[Pheasant] Start conversion: %s", source)
    pheasant_config["source_file"] = source
    source = read_source(source)  # Now source is always `str`.
    source = converter.convert(source)
    logger.debug("[Pheasant] End conversion: %s", pheasant_config["source_file"])
    return source

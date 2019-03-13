import importlib
import logging
import os
import re
import typing
from typing import (Any, Callable, Dict, Iterable, List, Match, Optional,
                    Tuple, Union)

from pheasant.utils import read_source

logger = logging.getLogger("mkdocs")
Call = Callable[[Dict[str, str]], Iterable[str]]
Dist = Union[str, Tuple[Callable, Dict[str, str]]]


class Renderer:
    flags = re.MULTILINE | re.DOTALL

    def __init__(self):
        self.patterns: List[str] = []
        self.calls: Dict[str, Call] = {}
        self.clients: Dict[str, Client] = {}
        self.pattern: Optional[typing.Pattern] = None

    def register(self, name: str, pattern: str, call: Call, client: "Client") -> None:
        self.patterns.append(f"(?P<{name}>{pattern})")
        self.calls[name] = call
        self.clients[name] = client

    def compile(self) -> typing.Pattern:
        pattern = "|".join(self.patterns)
        self.pattern = re.compile(pattern, self.flags)
        return self.pattern

    def render(self, source: str) -> Iterable[str]:
        self.generator = self.parse(source)
        for value in self.generator:
            if isinstance(value, str):
                yield value
            else:
                call, context = value
                yield from call(context)

    def parse(self, source: str) -> Iterable[Dist]:
        if self.pattern is None:
            pattern = self.compile()
        else:
            pattern = self.pattern

        cursor = 0
        for match in pattern.finditer(source):
            start, end = match.start(), match.end()
            if cursor < start:
                yield source[cursor:start]
            yield self.distribute(match)
            cursor = end
        if cursor < len(source):
            yield source[cursor:]

    def distribute(self, match: Match) -> Dist:
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
        if self.clients[key].enable:
            return self.calls[key], context
        else:
            return match.group()


class Converter:
    renderer = Renderer()

    def __init__(self):
        self.clients: Dict[str, Client] = {}

    def convert(self, source: str) -> str:
        return "".join(self.renderer.render(source))


converter = Converter()


class Client:
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.enable = True
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
                else:
                    default_config[key] = config[key]
        self.config = default_config
        self.converter = converter
        self.renderer = converter.renderer
        converter.clients[name] = self

    def register(self, name: str, pattern: str, call: Call) -> None:
        if self.renderer:
            name_pattern = r"\(\?P<(.+?)>(.+?)\)"
            replace = f"(?P<{self.name}__{name}__\\1>\\2)"
            pattern = re.sub(name_pattern, replace, pattern)
            name_pattern = r"\(\?P=(.+?)\)"
            replace = f"(?P={self.name}__{name}__\\1)"
            pattern = re.sub(name_pattern, replace, pattern)
            self.renderer.register(f"{self.name}__{name}", pattern, call, self)

    # def set_template(self, prefix_list:Optiona[List[str]]=None) -> None:
    #     default_directory = os.path.join(os.path.dirname(__file__), "templates")
    #     for prefix in ["fenced_code", "inline_code", "escaped_code"]:
    #         if prefix + "_template" in self.config:
    #             continue
    #         abspath = os.path.abspath(self.config[prefix + "_template_file"])
    #         logger.info(f'[Pheasant.jupyter] Template path "{abspath}" for {prefix}.')
    #         template_directory, template_file = os.path.split(abspath)
    #         loader = FileSystemLoader([template_directory, default_directory])
    #         env = Environment(loader=loader, autoescape=False)
    #         self.config[prefix + "_template"] = env.get_template(template_file)
    #
    # def set_template(self):
    #     default_directory = os.path.join(os.path.dirname(__file__), "templates")
    #
    #     abspath = os.path.abspath(self.config["template_file"])
    #     template_directory, template_file = os.path.split(abspath)
    #     env = Environment(
    #         loader=FileSystemLoader([template_directory, default_directory]),
    #         autoescape=False,
    #     )
    #     self.config["template"] = env.get_template(template_file)
    #


def start_client(name: str, config: Optional[Dict[str, Any]] = None) -> None:
    logger.info("[Pheasant.%s] Enabled", name)
    module = importlib.import_module(f"pheasant.{name}.client")
    Client = getattr(module, name[0].upper() + name[1:])
    print("===============", config)
    client = Client(config)
    for key, value in client.config.items():
        logger.debug("[Pheasant.%s] Config value: '%s' = %r", name, key, value)


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
    source = read_source(source)
    source = converter.convert(source)
    logger.debug("[Pheasant] End conversion: %s", pheasant_config["source_file"])
    return source

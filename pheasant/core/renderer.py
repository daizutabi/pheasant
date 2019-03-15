import importlib
import os
from typing import Any, Dict, List, Optional, Union

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from pheasant.core.parser import Render

Context = Dict[str, str]
Config = Dict[str, Any]


class Renderer:
    def __init__(self, config: Optional[Config] = None):
        self.renders: Dict[str, Render] = {}
        self.config: Dict[str, Any] = {}
        self.load_config()
        self.update_config(config)

    def __repr__(self):
        return f"<{self.__class__.__qualname__}[{len(self.renders)}])>"

    def register(self, pattern: str, render: Render) -> None:
        self.renders[pattern] = render

    def init(self) -> None:
        """Called once on build."""
        pass

    def reset(self) -> None:
        """Called per page."""
        pass

    def set_template(self, prefix: Union[str, List[str]] = "") -> None:
        module = importlib.import_module(self.__module__)
        default_directory = os.path.join(os.path.dirname(module.__file__), "templates")
        if isinstance(prefix, str):
            prefix = [prefix]
        for prefix_ in [f"{p}_" if p else "" for p in prefix]:
            template = f"{prefix_}template"
            template_file = f"{template}_file"
            abspath = os.path.abspath(self.config[template_file])
            template_directory, template_file = os.path.split(abspath)
            loader = FileSystemLoader([template_directory, default_directory])
            env = Environment(loader=loader, autoescape=select_autoescape(["jinja2"]))
            self.config[template] = env.get_template(template_file)

    def load_config(self, path: Optional[str] = None) -> None:
        if path is None:
            module = importlib.import_module(self.__module__)
            path = os.path.join(os.path.dirname(module.__file__), "config.yml")
        if os.path.exists(path):
            with open(path, "r") as f:
                config = yaml.load(f)
            self.update_config(config)

    def update_config(self, config: Optional[Config]) -> None:
        if config is None:
            return
        for key, value in config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, list):
                self.config[key].extend(value)
            elif isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value

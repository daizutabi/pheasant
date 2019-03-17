import importlib
import os
from dataclasses import field
from typing import Dict, List, Union

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from pheasant.core.base import Base
from pheasant.core.parser import Render  # type, not class


class Renderer(Base):
    renders: Dict[str, Render] = field(default_factory=dict)

    def __post_init__(self) -> None:
        super().__post_init__()
        module = importlib.import_module(self.__module__)
        path = os.path.join(os.path.dirname(module.__file__), "config.yml")
        if os.path.exists(path):
            with open(path, "r") as f:
                config = yaml.load(f)
            self.update_config(config)

    def __post_repr__(self):
        return len(self.renders)

    def register(self, pattern: str, render: Render) -> None:
        self.renders[pattern] = render

    def init(self) -> None:
        """Called once on build."""
        pass

    def reset(self) -> None:
        """Called per page."""
        pass

    def set_template(
        self, prefix: Union[str, List[str]] = "", directory: str = "templates"
    ) -> None:
        module = importlib.import_module(self.__module__)
        default_directory = os.path.join(os.path.dirname(module.__file__), directory)
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

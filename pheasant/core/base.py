from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(repr=False)
class Base:
    name: str = field(default="")
    config: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.name = self.name or self.__class__.__qualname__.lower()

    def __repr__(self):
        post = self.__post_repr__()
        post = f"[{post}]" if post else ""
        return f"<{self.__class__.__qualname__}#{self.name}{post}>"

    def __post_repr__(self):
        return ""

    def update_config(self, config: Dict[str, Any]) -> None:
        for key, value in config.items():
            if key not in self.config:
                self.config[key] = value
            elif isinstance(value, list):
                self.config[key].extend(value)
            elif isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value

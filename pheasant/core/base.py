from dataclasses import dataclass, field
from typing import Any, Dict


class MetaClass(type):
    def __new__(cls, name, bases, dict):
        decorator = dataclass(repr=False, eq=False)
        return decorator(type.__new__(cls, name, bases, dict))


class Base(metaclass=MetaClass):
    name: str = field(default="")
    config: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        self.name = self.name or self.__class__.__name__.lower()

    def __repr__(self):
        post = self.__post_repr__()
        post = f"[{post}]" if post else ""
        return f"<{self.__class__.__name__}#{self.name}{post}>"

    def __post_repr__(self):
        return ""

    def _update(self, name, update: Dict[str, Any]) -> None:
        arg = getattr(self, name)
        for key, value in update.items():
            if key not in arg:
                arg[key] = value
            elif isinstance(value, list):
                arg[key].extend(value)
            elif isinstance(value, dict):
                arg[key].update(value)
            else:
                arg[key] = value

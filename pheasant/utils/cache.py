import os
import pickle
from dataclasses import dataclass
from typing import Any


def cache_path(path: str) -> str:
    directory, path = os.path.split(path)
    return os.path.join(directory, ".pheasant_cache", path + ".cache")


def has_cache(path: str) -> bool:
    return os.path.exists(cache_path(path))


def modified(path: str) -> bool:
    if not has_cache(path):
        return True
    else:
        return os.stat(path).st_mtime > os.stat(cache_path(path)).st_mtime


def save(path: str, obj: Any) -> str:
    path = cache_path(path)
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.mkdir(directory)
    with open(path, "wb") as f:
        pickle.dump(obj, f)
    return path


def load(path: str) -> Any:
    path = cache_path(path)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None


def delete(path: str) -> None:
    path = cache_path(path)
    os.remove(path)


@dataclass
class Cache:
    path: str
    cache_path: str = ""
    modified: bool = False
    size: int = 0

    def __post_init__(self):
        self.cache_path = cache_path(self.path)
        self.has_cache = has_cache(self.path)
        self.modified = modified(self.path)
        if self.has_cache:
            self.size = os.path.getsize(self.cache_path)

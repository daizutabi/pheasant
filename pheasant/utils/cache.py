import os
import pickle
from typing import Any


def cache_path(path: str) -> str:
    directory, path = os.path.split(path)
    return os.path.join(directory, ".pheasant_cache", path + ".cache")


def has_cache(path: str) -> bool:
    return os.path.exists(cache_path(path))


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


def modified(path: str) -> bool:
    if not has_cache(path):
        return True
    else:
        return os.stat(path).st_mtime > os.stat(cache_path(path)).st_mtime

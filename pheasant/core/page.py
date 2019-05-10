import io
import os
import pickle
from dataclasses import dataclass, field
from typing import Any, Dict, List


def cache_path(path: str) -> str:
    directory, path = os.path.split(path)
    return os.path.join(directory, ".pheasant_cache", path + ".cache")


@dataclass
class Cache:
    page_path: str = field(default="", init=False)

    @property
    def path(self) -> str:
        return cache_path(self.page_path)

    @property
    def size(self) -> float:
        if os.path.exists(self.path):
            return os.path.getsize(self.path)
        else:
            return 0.0

    def save(self, obj: Any) -> str:
        directory = os.path.dirname(self.path)
        if not os.path.exists(directory):
            os.mkdir(directory)
        with open(self.path, "wb") as f:
            pickle.dump(obj, f)
        return self.path

    def load(self) -> Any:
        if os.path.exists(self.path):
            with open(self.path, "rb") as f:
                return pickle.load(f)
        return None

    def delete(self) -> None:
        if os.path.exists(self.path):
            os.remove(self.path)


@dataclass
class Page:
    path: str = ""
    source: str = field(default="", init=False)
    st_mtime: float = field(default=0.0, init=False)
    meta: Dict[str, Any] = field(default_factory=dict, init=False)
    cache: Cache = field(default_factory=Cache, init=False)

    def __post_init__(self):
        self.cache.page_path = self.path

    def read(self) -> str:
        with io.open(self.path, "r", encoding="utf-8-sig", errors="strict") as f:
            self.source = f.read()
        return self.source

    @property
    def has_cache(self) -> bool:
        return os.path.exists(self.cache.path)

    @property
    def modified(self) -> bool:
        if not self.has_cache:
            return True
        else:
            return os.stat(self.path).st_mtime > os.stat(self.cache.path).st_mtime


@dataclass
class Pages:
    roots: List[str]
    ext: str

    def __post_init__(self):
        if not self.roots:
            self.roots = ["."]

    def collect(self) -> List[Page]:
        exts = self.ext.split(",")
        pages = []

        def collect(path):
            if os.path.splitext(path)[-1][1:] in exts:
                pages.append(Page(os.path.normpath(path)))

        for root in self.roots:
            if os.path.isdir(root):
                for dirpath, dirnames, filenames in os.walk(root):
                    for file in filenames:
                        collect(os.path.join(dirpath, file))
            else:
                collect(root)
        return pages

import io
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Page:
    path: str = ""
    source: str = ""
    meta: Dict[str, Any] = field(default_factory=dict, init=False)
    st_mtime: float = 0.0

    def read(self, path: str = "") -> "Page":
        if path:
            self.path = path
        if self.path:
            with io.open(self.path, "r", encoding="utf-8-sig", errors="strict") as f:
                self.source = f.read()
        return self

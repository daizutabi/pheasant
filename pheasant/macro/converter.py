import re
from typing import Dict, Iterator

from pheasant.macro.config import config
from pheasant.utils import read_source


def initialize():
    pass


def convert(source: str) -> str:
    source = read_source(source)
    return convert_macro(source)


def convert_macro(source: str) -> str:
    return "\n".join(render(source))


def render(source: str) -> Iterator[str]:
    macros: Dict[str, str] = {}

    def replace(m):
        macro = m.group(1)
        return macros.get(macro, "XXX")

    re_match = re.compile("^" + config["tag_pattern"] + ":(.+)$")
    re_sub = re.compile(config["tag_pattern"])
    lines = source.split("\n")
    for line in lines:
        m = re_match.match(line)
        if m:
            macros[m.group(1)] = m.group(2).strip()
        else:
            yield re_sub.sub(replace, line)

import re
from typing import Dict, Iterator

from pheasant.jupyter.converter import initialize as initialize_jupyter
from pheasant.jupyter.preprocess import preprocess_markdown
from pheasant.macro.config import config
from pheasant.utils import read_source


def initialize():
    initialize_jupyter()
    config["TAG_DEF_PATTERN"] = re.compile("^" + config["tag_pattern"] + ":(.+)$")
    config["TAG_PATTERN"] = re.compile(config["tag_pattern"])


def convert(source: str) -> str:
    source = read_source(source)
    return convert_macro(source)


def convert_macro(source: str) -> str:
    return "\n".join(render(source))


def render(source: str) -> Iterator[str]:
    macros: Dict[str, str] = {}

    def replace(match):
        tag = match.group(1)
        if tag.startswith('#'):
            return match.group().replace('#', '')
        else:
            return macros.get(tag, "XXX")

    lines = source.split("\n")
    for line in lines:
        match = re.match(config["TAG_DEF_PATTERN"], line)
        if match:
            tag = match.group(1)
            if tag.startswith('#'):
                yield line.replace('#', '')
            else:
                macros[tag] = preprocess_markdown(match.group(2).strip())
        else:
            yield re.sub(config["TAG_PATTERN"], replace, line)

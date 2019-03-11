import re

from pheasant.code.config import config
from pheasant.code.fenced import convert as convert_fenced
from pheasant.code.inspect import convert as convert_inspect


def initialize():
    config["CODE_PATTERN"] = re.compile(config["code_pattern"])


def convert(source: str) -> str:
    source = convert_inspect(source)
    source = convert_fenced(source)
    return source

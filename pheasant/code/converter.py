from pheasant.code.fenced import convert as convert_fenced
from pheasant.code.inspect import convert as convert_inspect


def initialize():
    pass


def convert(source: str) -> str:
    source = convert_inspect(source)
    source = convert_fenced(source)
    return source

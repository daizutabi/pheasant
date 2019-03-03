from pheasant.code.fenced import convert as convert_fenced
from pheasant.code.inspect import convert as convert_inspect
from pheasant.utils import read_source


def initialize():
    pass


def convert(source: str) -> str:
    source = read_source(source)
    source = convert_inspect(source)
    source = convert_fenced(source)
    return source

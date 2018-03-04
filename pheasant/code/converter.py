from pheasant.utils import read_source

from .hilite import convert as convert_hilite
from .inspect import convert as convert_inspect


def initialize():
    pass


def convert(source: str) -> str:
    source = read_source(source)
    source = convert_inspect(source)
    source = convert_hilite(source)
    return source

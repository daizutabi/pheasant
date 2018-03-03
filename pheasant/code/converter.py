# from ..utils import read_source
from pheasant.utils import read_source
from .inspect import convert as convert_inspect
from .hilite import convert as convert_hilite


def initialize():
    pass


def convert(source: str):
    source = read_source(source)
    source = convert_inspect(source)
    source = convert_hilite(source)
    return source

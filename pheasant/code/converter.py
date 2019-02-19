from pheasant.code.html import convert as convert_html
from pheasant.code.inspect import convert as convert_inspect
from pheasant.utils import read_source


def initialize():
    pass


def convert(source: str) -> str:
    source = read_source(source)
    source = convert_inspect(source)
    source = convert_html(source)
    return source

from pheasant.core.base import Base
from pheasant.core.parser import Parser


def decorate(cell):
    if cell.match is None:
        cell.output = "<" + cell.output + ">"
    else:
        cell.output = "{" + cell.output + "}"


class A(Base):
    pattern_a = r"(?P<a>a)"
    pattern_b = r"(?P<b>b)"

    def render_a(self, context, splitter, parser):
        cell = next(splitter)
        if cell.match is not None:
            yield "[" + "".join(cell.render(cell.context, splitter, parser)) + "]"
        else:
            source = cell.source
            yield from parser.parse("b" + source, decorate=decorate)

    def render_b(self, context, splitter, parser):
        yield "B"


def test_core_parse_with_decorate():
    parser = Parser()
    a = A()
    parser.register(a.pattern_a, a.render_a)
    parser.register(a.pattern_b, a.render_b)

    source = "a12aa345"
    converter = parser.parse(source)
    next(converter) == "{B}<12>"
    next(converter) == "[{B}<345>]"

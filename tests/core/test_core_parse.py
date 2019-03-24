from pheasant.core.base import Base
from pheasant.core.parser import Parser


class A(Base):
    pattern_d = r"(?P<d>\d)"
    pattern_w = r"(?P<s>[a-z])"

    def render_digit(self, context, splitter, parser):
        yield context["d"]

    def render_word(self, context, splitter, parser):
        x = context["s"]
        if x == "a":
            yield x
        elif x == "b":
            cell = next(splitter)
            if cell.match is None:
                yield cell.source + x
            else:
                yield "[" + "".join(cell.render(cell.context, splitter, parser)) + "]"
        elif x == "c":
            yield parser.parse("b4")


def test_core_parse():
    parser = Parser()
    a = A()
    parser.register(a.pattern_d, a.render_digit)

    source = "123456789"
    assert parser.parse(source) == source


def test_core_parse_complex():
    parser = Parser()
    a = A()
    parser.register(a.pattern_d, a.render_digit)
    parser.register(a.pattern_w, a.render_word)

    source = "1a b2b abb 3bbacb5"
    assert parser.parse(source) == "1a [2] ba[ b]3[[a]][4][5]"


def decorate(cell):
    if cell.match is None:
        cell.output = "<" + cell.output + ">"
    else:
        cell.output = "{" + cell.output + "}"


class B(Base):
    pattern_a = r"(?P<a>a)"
    pattern_b = r"(?P<b>b)"

    def render_a(self, context, splitter, parser):
        cell = next(splitter)
        if cell.match is not None:
            yield "[" + "".join(cell.render(cell.context, splitter, parser)) + "]"
        else:
            source = cell.source
            yield parser.parse("b" + source, decorate=decorate)

    def render_b(self, context, splitter, parser):
        yield "B"


def test_core_parse_with_decorate():
    parser = Parser()
    a = B()
    parser.register(a.pattern_a, a.render_a)
    parser.register(a.pattern_b, a.render_b)

    source = "a12aa345"
    assert parser.parse(source) == "{B}<12>[{B}<345>]"

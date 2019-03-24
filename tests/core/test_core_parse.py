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
            yield from parser.parse("b4")


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

from pheasant.core.base import Base
from pheasant.core.parser import Parser


class A(Base):
    pattern_d = r"(?P<d>\d)"
    pattern_w = r"(?P<s>[a-z])"

    def render_digit(self, context, splitter):
        yield context.group.d

    def render_word(self, context, splitter):
        x = context.group.s
        if x == "a":
            yield x
        elif x == "b":
            context = next(splitter)
            if context.source is not None:
                yield context.source + x
            else:
                yield "[" + "".join(context.render(context, splitter)) + "]"
        elif x == "c":
            yield from context.parser.parse("bba")


def test_core_parse():
    parser = Parser()
    a = A()
    parser.register(a.pattern_d, a.render_digit)

    source = "123456789"
    converter = parser.parse(source)
    assert next(converter) == "1"
    assert next(converter) == "2"
    assert next(converter) == "3"
    assert next(converter) == "4"
    converter2 = parser.parse(source)
    assert next(converter2) == "1"
    assert next(converter) == "5"
    assert next(converter2) == "2"
    assert next(converter) == "6"


def test_core_parse_complex():
    parser = Parser()
    a = A()
    parser.register(a.pattern_w, a.render_word)

    source = "1ab2babb3bbacb4"
    converter = parser.parse(source)
    assert next(converter) == "1"
    assert next(converter) == "a"
    assert next(converter) == "2b"
    assert next(converter) == "[a]"
    assert next(converter) == "[3b]"
    assert next(converter) == "[[a]]"
    assert next(converter) == "[[a]]"
    assert next(converter) == "4b"

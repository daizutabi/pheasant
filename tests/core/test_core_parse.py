from pheasant.core.base import Base
from pheasant.core.parser import Parser


class A(Base):
    pattern_d = r"(?P<d>\d)"
    pattern_w = r"(?P<s>[a-z])"

    def render_digit(self, context, parser):
        yield context._source

    def render_word(self, context, parser):
        x = context._source
        if x == "a":
            yield x
        elif x == "b":
            cell = next(parser)
            print(cell.source if cell.source else cell.context._source)
            if cell.source is not None:
                yield cell.source + x
            else:
                yield "[" + "".join(cell.render(cell.context, parser)) + "]"
        elif x == "c":
            yield from parser.parse("bbx")


parser = Parser()
a = A()
parser.register(a.pattern_w, a.render_word)

source = "1ab2babb3bbacab4"
converter = parser.parse(source)
assert not hasattr(parser, "splitter")
assert next(converter) == "1"
assert next(converter) == "a"
assert next(converter) == "2b"
assert next(converter) == "[a]"
assert next(converter) == "[3b]"
assert next(converter) == "[[a]]"
assert next(converter) == "[[]]"
assert next(converter) == "a"


next(converter)


def test_core_parse():
    parser = Parser()
    a = A()
    parser.register(a.pattern_d, a.render_digit)

    source = "123456789"
    converter = parser.parse(source)
    assert not hasattr(parser, "splitter")
    assert next(converter) == "1"
    assert hasattr(parser, "splitter")
    assert next(parser).context._source == "2"
    assert next(parser.splitter).context._source == "3"
    assert next(converter) == "4"
    converter2 = parser.parse(source)
    assert next(converter2) == "1"
    assert next(converter) == "5"
    assert next(converter2) == "2"
    assert next(converter) == "6"
    assert next(parser).context._source == "3"
    assert next(converter) == "7"
    assert next(parser).context._source == "4"
    assert next(converter2) == "5"

    "".join(parser.parse(source))
    # parser.splitter is None


#     next(parser)
#
#
#
#     cell = next(splitter)
#     assert repr(cell) == "Cell(source='a ', match=None)"
#     cell = next(splitter)
#     cell
#
#     assert cell.source is None
#     assert cell.match is not None
#     assert list(cell.render(cell.context, parser)) == ["ba"]
#     cell = next(splitter)
#     cell = next(splitter)
#     assert cell.source is None
#     assert cell.match is not None
#     assert "".join(cell.render(cell.context, parser)) == "dc"
#
#
# def test_parse(parser):
#     source = "ef aa efab gh end"
#     assert "".join(parser.parse(source)) == " aa efbaab XXba dc end"

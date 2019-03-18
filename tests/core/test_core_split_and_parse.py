import pytest

from pheasant.core.base import Base
from pheasant.core.parser import Parser


class Renderer_A(Base):
    pattern_ab = r"(?P<a>a)(?P<b>b)"
    pattern_cd = r"(?P<c>c)(?P<d>d)"

    def render_ab(self, context, parser):
        yield "ba"

    def render_cd(self, context, parser):
        yield "dc"


class Renderer_B(Base):
    pattern_ef = r"(?P<e>e)(?P<f>f)"
    pattern_gh = r"(?P<g>g)(?P<h>h)"

    def render_ef(self, context, parser):
        cell = next(parser)
        if cell.match is None:
            yield cell.source
            yield context._source
        else:
            yield cell.convert()
            yield cell.context._source

    def render_gh(self, context, parser):
        yield "XX"
        yield from parser.parse('ab cd')


@pytest.fixture()
def a():
    a = Renderer_A()
    return a


@pytest.fixture()
def b():
    b = Renderer_B()
    return b


@pytest.fixture()
def parser(a, b):
    parser = Parser()
    parser.register(a.pattern_ab, a.render_ab)
    parser.register(a.pattern_cd, a.render_cd)
    parser.register(b.pattern_ef, b.render_ef)
    parser.register(b.pattern_gh, b.render_gh)
    return parser


def test_register(parser):
    assert len(parser.patterns) == 4
    assert len(parser.renders) == 4
    assert len(parser.context_classes) == 4
    assert len(parser.cell_classes) == 4
    keys = list(parser.patterns.keys())
    assert keys == [
        "renderer_a__ab",
        "renderer_a__cd",
        "renderer_b__ef",
        "renderer_b__gh",
    ]


def test_split(parser):
    source = "a ab ba cd dc ef fe gh"
    splitter = parser.split(source)
    cell = next(splitter)
    assert repr(cell) == "Cell(source='a ', match=None)"
    cell = next(splitter)
    assert cell.source == "ab"
    assert cell.match is not None
    assert list(cell.render(cell.context, parser)) == ["ba"]
    cell = next(splitter)
    cell = next(splitter)
    assert cell.source == "cd"
    assert cell.match is not None
    assert cell.convert() == "dc"


def test_parse(parser):
    source = "ef aa efab gh end"
    assert "".join(parser.parse(source)) == ' aa efbaab XXba dc end'

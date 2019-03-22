from pheasant.core.base import Base
from pheasant.core.parser import Parser


class Renderer_A(Base):
    pattern_ab = r"(?P<a>a)(?P<b>b)"
    pattern_cd = r"(?P<c>c)(?P<d>d)"

    def render_ab(self, context, splitter, parser):
        yield "ba"

    def render_cd(self, context, splitter, parser):
        yield "dc"


def test_split():
    a = Renderer_A()
    parser = Parser()
    parser.register(a.pattern_ab, a.render_ab)
    parser.register(a.pattern_cd, a.render_cd)
    assert len(parser.patterns) == 2
    assert len(parser.renders) == 2
    assert len(parser.cell_classes) == 2
    keys = list(parser.patterns.keys())
    assert keys == ["renderer_a__ab", "renderer_a__cd"]

    source = "a ab ba cd dc a ab a ab a ab"
    splitter = parser.split(source)
    cell = next(splitter)
    assert repr(cell) == "Cell(source='a ', match=None, output='')"
    cell = next(splitter)
    assert cell.match is not None
    assert list(cell.render(cell.context, splitter, parser)) == ["ba"]
    cell = next(splitter)
    cell = next(splitter)
    assert cell.match is not None
    assert "".join(cell.render(cell.context, splitter, parser)) == "dc"
    assert splitter.send('a ab') is None
    cell = next(splitter)
    assert repr(cell) == "Cell(source='a ', match=None, output='')"
    cell = next(splitter)
    assert cell.match is not None
    assert list(cell.render(cell.context, splitter, parser)) == ["ba"]

from pheasant.core.base import Base
from pheasant.core.parser import Parser


class Renderer_A(Base):
    pattern_ab = r"(?P<a>a)(?P<b>b)"
    pattern_cd = r"(?P<c>c)(?P<d>d)"

    def render_ab(self, context, splitter):
        yield "ba"

    def render_cd(self, context, splitter):
        yield "dc"


def test_split():
    a = Renderer_A()
    parser = Parser()
    parser.register(a.pattern_ab, a.render_ab)
    parser.register(a.pattern_cd, a.render_cd)
    assert len(parser.patterns) == 2
    assert len(parser.renders) == 2
    assert len(parser.group_classes) == 2
    assert len(parser.context_classes) == 2
    keys = list(parser.patterns.keys())
    assert keys == ["renderer_a__ab", "renderer_a__cd"]

    source = "a ab ba cd dc"
    splitter = parser.split(source)
    context = next(splitter)
    assert repr(context) == "Context(source='a ', match=None)"
    context = next(splitter)
    assert context.source is None
    assert context.match is not None
    assert list(context.render(context, splitter)) == ["ba"]
    context = next(splitter)
    context = next(splitter)
    assert context.source is None
    assert context.match is not None
    assert "".join(context.render(context, splitter)) == "dc"

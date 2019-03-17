import pytest


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(["begin\npy{{a=1}}e{{a;b}}end"])
    return source_simple


def test_render_inline_code(parser, jupyter, source_simple):
    splitter = parser.split(source_simple)
    next(splitter)
    cell = next(splitter)
    assert cell.context == {"code": "a=1", "_source": cell.source}
    next(splitter)
    cell = next(splitter)
    assert cell.context == {"code": "a;b", "_source": cell.source}

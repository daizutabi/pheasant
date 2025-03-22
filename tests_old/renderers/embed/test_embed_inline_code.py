import pytest


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        ["{%abc%}"]
    )
    return source_simple


def test_render_inline_code(parser, embed, source_simple):
    splitter = parser.split(source_simple)
    cell = next(splitter)
    assert cell.render_name == "embed__inline_code"

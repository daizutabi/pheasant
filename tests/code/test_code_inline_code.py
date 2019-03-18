import pytest


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        ["![file](abc)", "#![file](abc)", "![python](abc)", "#![python](abc)", "end"]
    )
    return source_simple


def test_render_inline_code(parser, code, source_simple):
    splitter = parser.split(source_simple)
    cell = next(splitter)
    assert cell.render_name == "code__inline_code"
    assert cell.context.language == "file"
    cell = next(splitter)
    assert cell.context.header == "#"
    cell = next(splitter)
    assert cell.context.source == "abc"

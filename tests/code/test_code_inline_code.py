import pytest


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        ["![file](abc)", "#![file](abc)", "![python](abc)", "#![python](abc)", "end"]
    )
    return source_simple


def test_render_inline_code(parser, code, source_simple):
    splitter = parser.split(source_simple)
    context = next(splitter)
    assert context.render_name == "code__inline_code"
    assert context.group.language == "file"
    context = next(splitter)
    assert context.group.header == "#"
    context = next(splitter)
    assert context.group.source == "abc"

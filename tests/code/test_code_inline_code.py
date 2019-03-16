import pytest


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        ["![file](abc)", "#![file](abc)", "![python](abc)", "#![python](abc)", "end"]
    )
    return source_simple


def test_render_inline_code(parser, code, source_simple):
    splitter = parser.splitter(source_simple)
    next(splitter)
    cell = splitter.send(dict)
    assert cell["name"] == "Code_render_inline_code"
    assert cell["context"] == {"header": "", "language": "file", "source": "abc"}
    cell = splitter.send(dict)
    assert cell["context"] == {"header": "#", "language": "file", "source": "abc"}
    cell = splitter.send(dict)
    assert cell["context"] == {"header": "", "language": "python", "source": "abc"}
    cell = splitter.send(dict)
    assert cell["context"] == {"header": "#", "language": "python", "source": "abc"}

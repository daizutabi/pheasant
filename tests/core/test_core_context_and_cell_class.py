import pytest

from pheasant.core.parser import make_cell_class, make_context_class


@pytest.fixture()
def pattern():
    return (
        r"^(?P<mark>`{3,})(?P<language>\w+) ?(?P<option>.*?)\n"
        r"(?P<code>.*?)\n(?P=mark)\n"
    )


@pytest.fixture()
def context_class(pattern):
    return make_context_class(pattern, "render_name")


@pytest.fixture()
def cell_class(context_class):
    return make_cell_class(context_class, "render_name", lambda context, parser: 0)


def test_core_make_context_class(context_class):
    context = context_class()
    assert context.mark == ""
    assert context.language == ""
    assert context.option == ""
    assert context.code == ""
    assert context._render_name == "render_name"
    assert context._source == ""


def test_core_make_cell_class(cell_class):
    cell = cell_class(source="Text")
    assert cell.source == "Text"
    assert cell.match is None
    assert cell.render_name == "render_name"

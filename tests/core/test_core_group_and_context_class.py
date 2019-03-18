import pytest

from pheasant.core.parser import make_context_class, make_group_class


@pytest.fixture()
def pattern():
    return (
        r"^(?P<mark>`{3,})(?P<language>\w+) ?(?P<option>.*?)\n"
        r"(?P<code>.*?)\n(?P=mark)\n"
    )


@pytest.fixture()
def group_class(pattern):
    return make_group_class(pattern)


@pytest.fixture()
def context_class(group_class):
    return make_context_class(group_class, "render_name", 4, 5)


def test_core_make_group_class(group_class):
    group = group_class()
    assert group.mark == ""
    assert group.language == ""
    assert group.option == ""
    assert group.code == ""


def test_core_make_context_class(context_class):
    context = context_class(source="Text", match=1, group=2)  # dummy data
    assert context.source == "Text"
    assert context.match == 1
    assert context.group == 2
    assert context.render_name == "render_name"
    assert context.render == 4
    assert context.parser == 5

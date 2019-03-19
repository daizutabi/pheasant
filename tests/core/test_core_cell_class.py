from pheasant.core.parser import make_cell_class


def func(context, spliter, parser):
    pass


def test_core_make_cell_class():
    cell_class = make_cell_class("pattern", func, "render_name")
    cell = cell_class("source", "match", {"a": "1"})
    assert cell.source == "source"
    assert cell.match == "match"
    assert cell.context == {"a": "1"}
    assert cell.render == func
    assert cell.render_name == "render_name"

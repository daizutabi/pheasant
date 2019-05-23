from pheasant.renderers.jupyter.jupyter import Jupyter


def test_cache():
    jupyter = Jupyter()
    assert jupyter.cache == []
    assert jupyter.count == 0

    context = {"code": "1", "b": "b", "language": "python", "option": ""}
    template = "fenced_code"
    output = jupyter.execute_and_render("1", context, template)
    assert jupyter.count == 1
    cache = jupyter.cache
    assert len(cache) == 1
    cell = cache[jupyter.count - 1]
    assert cell.output == output
    assert cell.valid

    jupyter.execute_and_render("2", context, template)
    jupyter.execute_and_render("3", context, template)
    jupyter.execute_and_render("4", context, template)

    assert jupyter.count == 4
    assert len(cache) == 4

    jupyter.count = 0

    output = jupyter.execute_and_render("1", context, template)
    assert "cached" in output

    output = jupyter.execute_and_render("2*2", context, template)
    assert "cached" not in output
    assert not cache[2].valid

    output = jupyter.execute_and_render("3", context, template)
    assert "cached" not in output
    assert not cache[3].valid

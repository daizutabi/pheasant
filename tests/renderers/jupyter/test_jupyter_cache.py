from pheasant.renderers.jupyter.jupyter import Jupyter


def test_cache():
    jupyter = Jupyter()
    assert jupyter.cache == {}
    assert jupyter.cursor == 0

    jupyter.abs_src_path = "test"
    context = {"a": "a", "b": "b", "language": "python"}
    template = "fenced_code"
    output = jupyter.execute_and_render("1", context, template)
    assert jupyter.cursor == 1
    assert 'test' in jupyter.cache
    cache = jupyter.cache['test']
    assert len(cache) == 1
    cell = cache[jupyter.cursor - 1]
    assert cell.output == output
    assert cell.valid

    jupyter.execute_and_render("2", context, template)
    jupyter.execute_and_render("3", context, template)
    jupyter.execute_and_render("4", context, template)

    assert jupyter.cursor == 4
    assert len(cache) == 4

    jupyter.reset()
    assert jupyter.cursor == 0
    assert len(cache) == 4

    output = jupyter.execute_and_render("1", context, template)
    assert "cached" in output

    output = jupyter.execute_and_render("2*2", context, template)
    assert "cached" not in output
    assert not cache[2].valid

    output = jupyter.execute_and_render("3", context, template)
    assert "cached" not in output
    assert not cache[3].valid

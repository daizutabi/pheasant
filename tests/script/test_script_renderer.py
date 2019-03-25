def test_renderer_config(script):
    assert script.config == {}


def test_render_script_without_process(script, source):
    assert script.convert(source, -1) == source


def test_render_script_fenced_code(script, source):
    output = script.convert(source, 0)
    source = source.split("# before:\n")[1:]
    output = output.split("before:\n")[1:]
    for k in [0, 1]:
        _, after = source[k].split("after:\n")
        before, _ = output[k].split("after:\n")
        assert after == before[10:-4]

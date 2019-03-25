def test_renderer_config(script):
    assert script.config == {}


def test_render_script(script, source):
    assert script.convert(source, -1) == source

    # print(script.parse(source))
    # assert script.parse(source) == source
    #
    # assert 0

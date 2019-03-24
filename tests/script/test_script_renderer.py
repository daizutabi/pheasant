def test_renderer_config(script):
    assert script.config == {}


def test_render_script(script, source):
    # script.comment.max_line_length = -1
    # assert script.parse(source) == source

    script.comment.max_line_length = 0
    print(script.parse(source))
    assert script.parse(source) == source

    assert 0

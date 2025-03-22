def test_renderer_config(script):
    assert script.config == {}


def test_render_script_fenced_code(script, source):
    output = script.convert(source, 0)
    source = source.split("# before:\n")[1:]
    output = output.split("before:\n")[1:]
    for k in [0, 1]:
        _, after = source[k].split("after:\n")
        before, _ = output[k].split("after:\n")
        assert after == before[10:-4]


# def test_render_script_option(script, source):
#     output = script.convert(source, 0)
#     print(output)
#     assert "```python display\n@pytest.fixture()\ndef script" in output
#     assert "```python inline display\ndef g()" in output


def test_render_markdown(script):
    assert script.convert("# ~~~\n# a\n# b\n# ~~~\n", 0) == "~~~\na\nb\n~~~\n"
    assert script.convert("# ~~~markdown\n# a\n# b\n# ~~~\n", 0) == "a\nb\n"


def test_render_hedader(script):
    assert script.convert('# # title\n# # and title\n') == "# # title and title\n"

def test_render_cell(script):
    source = "# a\n# %% [cell]\n# test\na=1\nb=1\n# %% [markdown]\n# a\n# b\n\n# c\n"
    answer = "```python\n# test\na=1\nb=1\n```\na b\n\nc\n"
    output = script.parse(source)
    print(output)
    assert output == answer

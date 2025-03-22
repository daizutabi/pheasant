import pytest


def inline_code(code):
    return "[{{" + code + "}}]"


@pytest.fixture()
def parse(jupyter):
    def func(code):
        return jupyter.parse(inline_code(code))

    return func


def test_jupyter_parse_text(parse):
    output = parse("print(1)")
    assert output == "[]"

    output = parse("1")
    assert output == '[1]'
    output = parse("'abc'")
    assert output == '[abc]'
    output = parse("a='abc';a")
    assert output == '[abc]'

    # output = parse("1/0")
    # answer = '[<span class="error">ZeroDivisionError: division by zero</span>]'
    # assert output == answer


def test_jupyter_parse_html(parse):
    output = parse("import pandas;pandas.DataFrame([[1,2]])")
    assert (
        '[\n\n<div class="cell jupyter display"><div class="content">'
        '<table class="dataframe' in output
    )


def test_jupyter_parse_png(parse):
    parse("import matplotlib.pyplot as plt")
    output = parse("plt.plot([1,2])")
    assert (
        '[\n\n<div class="cell jupyter display"><div class="content"><p>'
        '<img alt="image/png" src="data:image/png' in output
    )

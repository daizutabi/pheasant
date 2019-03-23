import pytest


def inline_code(code):
    return "[{{" + code + "}}]"


@pytest.fixture()
def parse(parser):
    def func(code):
        return "".join(parser.parse(inline_code(code)))

    return func


def test_jupyter_parse_text(parse):
    output = parse("print(1)")
    assert output == "[]"

    output = parse("1")
    assert output == '[<span class="output">1</span>]'
    output = parse("'abc'")
    assert output == '[<span class="output">abc</span>]'
    output = parse("a='abc';a")
    assert output == '[<span class="output">abc</span>]'

    output = parse("1/0")
    answer = '[<span class="error">ZeroDivisionError: division by zero</span>]'
    assert output == answer


def test_jupyter_parse_html(parse):
    output = parse("import pandas;pandas.DataFrame([[1,2]])")
    assert (
        '[\n\n<div class="display"><div class="content"><table class="dataframe'
        in output
    )


def test_jupyter_parse_png(jupyter, parse):
    jupyter.execute("import matplotlib.pyplot as plt")
    output = parse("plt.plot([1,2])")
    assert (
        '[\n\n<div class="display"><div class="content"><p>'
        '<img alt="image/png" src="data:image/png' in output
    )

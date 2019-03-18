from pheasant.jupyter.renderer import (preprocess_fenced_code,
                                       preprocess_inline_code)


def test_preprocess_inline_code():
    assert preprocess_inline_code("a=1") == "a=1"

    output = preprocess_inline_code("a")
    answer = 'pheasant.jupyter.display.display(a, output="markdown")'
    assert output == answer

    output = preprocess_inline_code("^a")
    answer = 'pheasant.jupyter.display.display(a, output="html")'
    assert output == answer


def test_preprocess_fenced_code():
    output = preprocess_fenced_code("a=1\n{{a}}")
    answer = 'a=1\npheasant.jupyter.display.display(a, output="markdown")'
    assert output == answer

    output = preprocess_fenced_code("a=1\n{{^a}}")
    answer = 'a=1\npheasant.jupyter.display.display(a, output="html")'
    assert output == answer

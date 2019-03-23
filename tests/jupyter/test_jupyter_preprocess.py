from pheasant.jupyter.renderer import (replace_fenced_code_for_display,
                                       replace_for_display)


def test_replace_for_display():
    assert replace_for_display("a=1") == "a=1"

    output = replace_for_display("a")
    answer = 'pheasant.jupyter.display.display(a, output="markdown")'
    assert output == answer

    output = replace_for_display("^a")
    answer = 'pheasant.jupyter.display.display(a, output="html")'
    assert output == answer


def test_replace_fenced_code_for_display():
    output = replace_fenced_code_for_display("a=1\n{{a}}")
    answer = 'a=1\npheasant.jupyter.display.display(a, output="markdown")'
    assert output == answer

    output = replace_fenced_code_for_display("a=1\n{{^a}}")
    answer = 'a=1\npheasant.jupyter.display.display(a, output="html")'
    assert output == answer

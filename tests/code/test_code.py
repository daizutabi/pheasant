import nbformat

from pheasant.code.html import escaped_code_splitter
from pheasant.code.inspect import convert
from pheasant.jupyter.client import run_cell
from pheasant.jupyter.converter import initialize


def test_inspect_convert():
    initialize()
    assert convert('abc') == 'abc'
    source = 'def func(x):\n    return x + 1\n'
    cell = nbformat.v4.new_code_cell(source)
    run_cell(cell)
    content = convert('![python](func)')
    answer = '<!-- begin -->\n```python .pheasant-markdown .pheasant-code\n'
    assert content.startswith(answer)
    answer = f'{source}```\n<!-- end -->\n'
    assert content.endswith(answer)

    source = '![dummy](func)'
    assert convert(source) == source


def test_escaped_code_splitter():
    splitter = escaped_code_splitter('a\nb')
    for k, splited in enumerate(splitter):
        if k == 0:
            assert splited == 'a\nb'
    assert k == 0

    splitter = escaped_code_splitter('~~~python\nprint(1)\n~~~\n\nabc')
    for k, splited in enumerate(splitter):
        if k == 0:
            assert splited == '~~~python\nprint(1)\n~~~\n'
        elif k == 1:
            assert splited == '\nabc'
    assert k == 1

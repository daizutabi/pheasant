import nbformat

from pheasant.code.inspect import convert, inspect_render
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

    source = '![python](print)'
    assert convert(source) == ''

    cell = nbformat.v4.new_code_cell('a = 1')
    assert inspect_render(cell, 'python') == ''

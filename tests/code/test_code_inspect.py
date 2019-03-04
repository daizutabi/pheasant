import nbformat

from pheasant.code.inspect import convert, inspect_render
from pheasant.jupyter.client import run_cell
from pheasant.jupyter.converter import initialize


def test_initialize():
    assert initialize() is None


def test_inspect_convert():
    assert convert('abc') == 'abc'
    source = 'def func(x):\n    return x + 1\n'
    cell = nbformat.v4.new_code_cell(source)
    run_cell(cell)
    content = convert('![python](func)')
    answer = '<!-- begin -->\n~~~python .pheasant-fenced-code .pheasant-code\n'
    assert content.startswith(answer)
    answer = f'{source}~~~\n<!-- end -->\n'
    assert content.endswith(answer)

    source = '![dummy](func)'
    assert convert(source) == source

    source = '![python](print)'
    assert convert(source) == ''

    cell = nbformat.v4.new_code_cell('a = 1')
    assert inspect_render(cell, 'python') == ''


def test_inspect_convert_with_header():
    content = convert('abc\n\n#![file](a.py)\n\ndef')
    answer = ('abc\n\n#File a.py\n<p style="font-color:red">'
              'File not found: a.py</p>\n\ndef')
    assert content == answer

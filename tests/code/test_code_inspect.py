from pheasant.code.inspect import convert
from pheasant.jupyter.client import execute
from pheasant.jupyter.converter import initialize


def test_initialize():
    assert initialize() is None


def test_inspect_convert():
    assert convert('abc') == 'abc'
    code = 'def func(x):\n    return x + 1\n'
    execute(code)
    content = convert('![python](func)')
    answer = '<!-- begin -->\n~~~python .pheasant-fenced-code .pheasant-code\n'
    assert content.startswith(answer)
    answer = f'{code}~~~\n<!-- end -->\n'
    assert content.endswith(answer)

    source = '![dummy](func)'
    assert convert(source) == source

    source = '![python](print)'
    assert convert(source) == ''


def test_inspect_convert_with_header():
    content = convert('abc\n\n#![file](a.py)\n\ndef')
    answer = ('abc\n\n#File a.py\n<p style="font-color:red">'
              'File not found: a.py</p>\n\ndef')
    assert content == answer

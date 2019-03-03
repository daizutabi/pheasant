from pheasant.code.html import convert, escaped_code, escaped_code_splitter


def test_convert():
    source = 'abc'
    assert convert(source) == source

    source = '```python\nprint(1)\n```\n'
    answer = '<div class=" codehilite"><pre><span></span><span class="k">'
    assert convert(source).startswith(answer)
    answer = '<span class="mi">1</span><span class="p">)</span>\n</pre></div>'
    assert convert(source).endswith(answer)

    source = '```display .test\n$$x=1$$\n```\n'
    assert convert(source) == '<div class="test">\n<p>$$x=1$$\n</p>\n</div>\n'

    source = '```display .test\na & b\n```\n'
    answer = '<div class="test">\n<p>a &amp; b</p>\n</div>\n'
    assert convert(source) == answer

    source = '~~~\n```python\nprint(1)\n```\n~~~\n'
    answer = '<div class="codehilite pheasant-fenced-code pheasant-source"><pre>'
    assert convert(source).startswith(answer)
    answer = '1</span><span class="p">)</span>\n<span>```</span>\n</pre></div>'
    assert convert(source).endswith(answer)


def test_escaped_code():
    answer = ('<div class="pheasant-fenced-code pheasant-code codehilite">'
              '<pre><span></span>source\n</pre></div>')
    assert escaped_code('abd', 'source', ['cls']) == answer


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

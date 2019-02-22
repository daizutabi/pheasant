from pheasant.code.html import convert, escaped_code_splitter


def test_convert():
    source = '```python\nprint(1)\n```\n'
    answer = '<div class=" codehilite"><pre><span></span><span class="k">'
    assert convert(source).startswith(answer)
    answer = '<span class="mi">1</span><span class="p">)</span>\n</pre></div>'
    assert convert(source).endswith(answer)


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

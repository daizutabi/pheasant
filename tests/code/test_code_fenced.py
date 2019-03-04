from pheasant.code.fenced import convert, escaped_code


def test_convert():
    source = 'abc'
    assert convert(source) == source

    source = '```python\nprint(1)\n```\n'
    answer = '<div>\n<pre><code class="python">print(1)\n</code></pre>\n</div>'
    assert convert(source)[:-1] == answer

    source = '```display .test\n$$x=1$$\n```\n'
    assert convert(source) == '<div class="test">\n<p>$$x=1$$\n</p>\n</div>\n'

    source = '```display .test\na & b\n```\n'
    answer = '<div class="test">\n<p>a &amp; b</p>\n</div>\n'
    assert convert(source) == answer

    source = '~~~\n```python\nprint(1)\n```\n~~~\n'
    output = convert(source)
    answer = '<div class="pheasant-fenced-code pheasant-source">\n<pre>'
    assert output.startswith(answer)
    answer = ('"markdown"><span class="pheasant-backquote">```</span>python\n'
              'print(1)\n<span class="pheasant-backquote">```</span>\n</code>'
              '</pre>\n</div>\n')
    assert output.endswith(answer)


def test_escaped_code():
    answer = ('<div class="class1 class2">\n'
              '<pre><code class="language">source</code></pre>\n</div>\n')
    assert escaped_code('language', 'source', ['.class1', '.class2']) == answer

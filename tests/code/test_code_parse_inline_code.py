import os

import pytest

from pheasant.jupyter.client import execute


def inline_code(header, language, source):
    return f"{header}![{language}]({source})\n"


@pytest.fixture()
def parse(parser):
    def func(header, language, source, pre="", post=""):
        if pre:
            pre += "\n"
        return "".join(parser.parse(pre + inline_code(header, language, source) + post))

    return func


@pytest.fixture()
def file(tmpdir, parse):
    def func(header, path, source):
        path_ = tmpdir.join(path)
        path_.write(source)
        current = os.path.abspath(os.path.curdir)
        os.chdir(tmpdir)
        output = parse(header, "file", path)
        os.chdir(current)
        return output

    return func


def test_code_parse_file(file):
    path = "hello.py"
    source = "def func(x):\n    return 2 * x\n\nprint(f(3))\n"
    output = file("", path, source)
    answer = (
        '<div class="source"><pre>'
        '<code class="python">def func(x):\n    return 2 * x\n\nprint(f(3))'
        "</code></pre></div>\n"
    )
    assert output == answer


def test_code_parse_file_not_founed(parse):
    path = "xxx.py"
    output = parse("", "file", path)
    assert output == '<p style="font-color:red">File not found: xxx.py</p>\n'


def test_code_parse_inspect(parse):
    execute("import pheasant")
    output = parse("", "python", "pheasant")
    answer = (
        '<div class="source">'
        '<pre><code class="python">__version__ ='
    )
    assert output.startswith(answer)


def test_code_parse_inspect_not_found(parse):
    output = parse("", "xxx", "xxx")
    assert output.startswith('<p><img alt="xxx"')


def test_code_parse_file_with_header(file):
    path = "hello.py"
    source = "def func(x):\n    return 2 * x\n\nprint(f(3))\n"
    output = file("#", path, source)
    assert output.startswith('<div class="file">')
    print(output)
    assert output.endswith('print(f(3))</code></pre></div>\n</div></div>\n')

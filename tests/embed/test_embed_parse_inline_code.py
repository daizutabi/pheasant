import os

import pytest

from pheasant.jupyter.client import execute


@pytest.fixture()
def parse(parser):
    def func(source):
        return parser.parse("{%" + source + "%}")

    return func


@pytest.fixture()
def file(tmpdir, parse):
    def func(path, source):
        path_ = tmpdir.join(path)
        path_.write(source)
        current = os.path.abspath(os.path.curdir)
        os.chdir(tmpdir)
        output = parse(path)
        os.chdir(current)
        return output

    return func


def test_code_parse_file(file):
    path = "hello.py"
    source = "def func(x):\n    return 2 * x\n\nprint(f(3))\n"
    output = file(path, source)
    answer = (
        '\n<div class="source"><pre>'
        '<code class="python">def func(x):\n    return 2 * x\n\nprint(f(3))'
        "</code></pre></div>\n\n"
    )
    assert output == answer


def test_code_parse_file_not_founed(parse):
    path = "xxx.py"
    output = parse(path)
    assert output == '<p style="font-color:red">File not found: xxx.py</p>\n'


def test_code_parse_inspect(parse):
    execute("import pheasant")
    output = parse("?pheasant")
    answer = '\n<div class="source">' '<pre><code class="python">__version__ ='
    assert output.startswith(answer)

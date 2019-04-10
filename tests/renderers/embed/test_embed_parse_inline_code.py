import os

import pytest

from pheasant.renderers.jupyter.client import execute


@pytest.fixture()
def parse(parser):
    def func(source):
        return parser.parse("{%" + source + "%}")

    return func


@pytest.fixture()
def file(tmpdir, parse):
    def func(path, content, source):
        path_ = tmpdir.join(path)
        path_.write(content)
        current = os.path.abspath(os.path.curdir)
        os.chdir(tmpdir)
        output = parse(source)
        os.chdir(current)
        return output

    return func


def test_embed_parse_file(file):
    path = "hello.py"
    content = "def func(x):\n    return 2 * x\n\nprint(f(3))\n"
    source = "=hello.py"
    output = file(path, content, source)
    answer = (
        '\n\n<div class="cell embed file"><div class="code"><pre>'
        '<code class="python">def func(x):\n    return 2 * x\n\nprint(f(3))'
        "</code></pre></div></div>\n\n"
    )
    assert output == answer


def test_embed_parse_file_not_founed(parse):
    path = "xxx.py"
    output = parse(path)
    assert '<p style="font-color:red">File not found:' in output


def test_embed_parse_inspect(parse):
    execute("import pheasant")
    output = parse("?pheasant")
    answer = ('\n\n<div class="cell embed file"><div class="code">'
              '<pre><code class="python">__version__ =')
    assert output.startswith(answer)

import pytest


def fenced_code(source):
    return f"~~~python\n{source}\n~~~\n"


@pytest.fixture()
def parse(parser):
    def func(source):
        return "".join(parser.parse(fenced_code(source)))

    return func


def test_code_parse_source(parse):
    output = parse("print(1)\na = 1")
    answer = "".join(
        [
            '<div class="pheasant-fenced-code pheasant-source">'
            '<pre><code class="python">print(1)\na = 1</code></pre></div>'
        ]
    )
    assert output == answer

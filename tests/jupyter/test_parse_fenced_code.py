import pytest


def fenced_code(code):
    return f"```python\n{code}\n```\n"


@pytest.fixture()
def parse(parser):
    def func(code):
        return "".join(parser.parse(fenced_code(code)))

    return func


def test_jupyter_template(jupyter):
    assert "fenced_code_template" in jupyter.config
    assert "inline_code_template" in jupyter.config


def test_jupyter_parse_text(parse):
    output = parse("print(1)")
    answer = "".join(
        [
            '<div class="pheasant-fenced-code pheasant-input">'
            '<pre><code class="python">print(1)</code></pre></div>'
            '<div class="pheasant-fenced-code pheasant-output">'
            '<pre><code class="python">1</code></pre></div>'
        ]
    )
    assert output == answer

    output = parse("1")
    answer = "".join(
        [
            '<div class="pheasant-fenced-code pheasant-input">'
            '<pre><code class="python">1</code></pre></div>'
            '<div class="pheasant-fenced-code pheasant-output">'
            '<pre><code class="python">1</code></pre></div>'
        ]
    )
    assert output == answer

    output = parse("'abc'")
    answer = "".join(
        [
            '<div class="pheasant-fenced-code pheasant-input">'
            '<pre><code class="python">&#39;abc&#39;</code></pre></div>'
            '<div class="pheasant-fenced-code pheasant-output">'
            '<pre><code class="python">&#39;abc&#39;</code></pre></div>'
        ]
    )
    assert output == answer

    output = parse("1/0")
    answer = "".join(
        [
            '<div class="pheasant-fenced-code pheasant-input">'
            '<pre><code class="python">1/0</code></pre></div>'
            '<div class="pheasant-fenced-code pheasant-error">'
            '<pre><code class="python">ZeroDivisionError: division by zero'
            "</code></pre></div>"
        ]
    )
    assert output == answer

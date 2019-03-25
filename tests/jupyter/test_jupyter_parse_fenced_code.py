import pytest


def fenced_code(code):
    return f"```python\n{code}\n```\n"


@pytest.fixture()
def parse(jupyter):
    def func(code):
        return jupyter.parser.parse(fenced_code(code))

    return func


def test_jupyter_template(jupyter):
    assert "fenced_code_template" in jupyter.config
    assert "inline_code_template" in jupyter.config


def test_jupyter_parse_text(parse):
    output = parse("print(1)")
    answer = "".join(
        [
            '<div class="input"><pre><code class="python">print(1)</code></pre></div>'
            '<div class="stdout"><pre><code class="python">1</code></pre></div>\n'
        ]
    )
    assert output == answer

    output = parse("1")
    answer = "".join(
        [
            '<div class="input"><pre><code class="python">1</code></pre></div>'
            '<div class="output"><pre><code class="python">1</code></pre></div>\n'
        ]
    )
    assert output == answer

    output = parse("'abc'")
    answer = "".join(
        [
            '<div class="input">'
            '<pre><code class="python">&#39;abc&#39;</code></pre></div>'
            '<div class="output">'
            '<pre><code class="python">&#39;abc&#39;</code></pre></div>\n'
        ]
    )
    assert output == answer

    output = parse("1/0")
    answer = "".join(
        [
            '<div class="input">'
            '<pre><code class="python">1/0</code></pre></div>'
            '<div class="error">'
            '<pre><code class="python">ZeroDivisionError: division by zero'
            "</code></pre></div>\n"
        ]
    )
    assert output == answer


def test_jupyter_parse_html(parse):
    output = parse("import pandas\npandas.DataFrame([[1,2]])")
    assert '<div class="display"><div>' in output


def test_jupyter_parse_png(parse):
    output = parse("import matplotlib.pyplot as plt")
    output = parse("plt.plot([1,2])")
    print(output)
    assert '<div class="output"><pre><code class="python">[&lt;matplot' in output
    assert '<div class="display"><p><img alt="image/png" src="data:image/png' in output

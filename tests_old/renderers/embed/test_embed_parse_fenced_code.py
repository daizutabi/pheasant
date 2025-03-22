import pytest


def fenced_code(language, source):
    return f"~~~{language}\n{source}\n~~~\n"


@pytest.fixture()
def parse(parser):
    def func(language, source, pre="", post=""):
        if pre:
            pre += "\n"
        return parser.parse(pre + fenced_code(language, source) + post)

    return func


def test_code_parse_source(parse):
    output = parse("python", "print(1)\na = 1")
    answer = "".join(
        [
            '\n<div class="cell embed source"><div class="code">'
            '<pre><code class="python">print(1)\na = 1</code></pre></div></div>\n\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy(parse):
    output = parse("copy", "text.")
    answer = "".join(
        [
            '\n<div class="cell embed source"><div class="code">'
            '<pre><code class="markdown">text.</code></pre></div></div>\n\ntext.\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_jupyter(parse):
    output = parse("copy", "```python\n2*3\n```")
    answer = "".join(
        [
            '\n<div class="cell embed source"><div class="code">'
            '<pre><code class="markdown">```python\n2*3\n```</code></pre></div>'
            '</div>\n\n\n<div class="input">'
            '<pre><code class="python">2*3</code></pre></div>'
            '<div class="output">'
            '<pre><code class="python">6</code></pre></div>\n\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_number(parse):
    output = parse("copy", "# Title\n## Section\nText")
    answer = "".join(
        [
            '\n<div class="cell embed source"><div class="code">'
            '<pre><code class="markdown"># Title\n## Section\nText</code></pre>'
            '</div></div>\n\n# <span class="header"><span class="number">1</span> '
            '<span class="title">Title</span></span>\n\n'
            '## <span class="header"><span class="number">1.1</span> '
            '<span class="title">Section</span></span>\n\nText\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_pre_post(parse):
    output = parse("copy", "text.", "pre", "post")
    answer = "".join(
        [
            'pre\n\n<div class="cell embed source"><div class="code">'
            '<pre><code class="markdown">text.</code></pre></div></div>\n\ntext.\npost'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_pre_post_jupyter(parse):
    output = parse("copy", "text.", "```python\n1\n```", "```python\n2\n```\n")
    answer = "".join(
        [
            '\n<div class="input">'
            '<pre><code class="python">1</code></pre></div>'
            '<div class="output">'
            '<pre><code class="python">1</code></pre></div>\n\n'
            '\n<div class="cell embed source"><div class="code">'
            '<pre><code class="markdown">text.</code></pre></div></div>\n\n'
            "text.\n"
            '\n<div class="input">'
            '<pre><code class="python">2</code></pre></div>'
            '<div class="output">'
            '<pre><code class="python">2</code></pre></div>\n\n'
        ]
    )
    assert output == answer

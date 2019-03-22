import pytest


def fenced_code(language, source):
    return f"~~~{language}\n{source}\n~~~\n"


@pytest.fixture()
def parse(parser):
    def func(language, source, pre="", post=""):
        if pre:
            pre += "\n"
        return "".join(parser.parse(pre + fenced_code(language, source) + post))

    return func


def test_code_parse_source(parse):
    output = parse("python", "print(1)\na = 1")
    answer = "".join(
        [
            '<div class="source">'
            '<pre><code class="python">print(1)\na = 1</code></pre></div>\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy(parse):
    output = parse("copy", "text.")
    answer = "".join(
        [
            '<div class="source">'
            '<pre><code class="markdown">text.</code></pre></div>\ntext.\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_jupyter(parse):
    output = parse("copy", "```python\n2*3\n```")
    answer = "".join(
        [
            '<div class="source">'
            '<pre><code class="markdown">```python\n2*3\n```</code></pre></div>\n'
            '<div class="input">'
            '<pre><code class="python">2*3</code></pre></div>'
            '<div class="output">'
            '<pre><code class="python">6</code></pre></div>\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_number(parse):
    output = parse("copy", "# Title\n## Section\nText")
    answer = "".join(
        [
            '<div class="source">'
            '<pre><code class="markdown"># Title\n## Section\nText</code></pre></div>\n'
            '# <span class="header"><span class="number">1</span> '
            '<span class="title">Title</span></span>\n'
            '## <span class="header"><span class="number">1.1</span> '
            '<span class="title">Section</span></span>\nText\n'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_pre_post(parse):
    output = parse("copy", "text.", "pre", "post")
    answer = "".join(
        [
            'pre\n<div class="source">'
            '<pre><code class="markdown">text.</code></pre></div>\ntext.\npost'
        ]
    )
    assert output == answer


def test_code_parse_source_copy_pre_post_jupyter(parse):
    output = parse("copy", "text.", "```python\n1\n```", "```python\n2\n```\n")
    answer = "".join(
        [
            '<div class="input">'
            '<pre><code class="python">1</code></pre></div>'
            '<div class="output">'
            '<pre><code class="python">1</code></pre></div>\n'
            '<div class="source">'
            '<pre><code class="markdown">text.</code></pre></div>\n'
            "text.\n"
            '<div class="input">'
            '<pre><code class="python">2</code></pre></div>'
            '<div class="output">'
            '<pre><code class="python">2</code></pre></div>\n'
        ]
    )
    assert output == answer

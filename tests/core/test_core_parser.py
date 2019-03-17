from typing import Match

import pytest

from pheasant.core.parser import Parser


def test_parser_without_pattern():
    parser = Parser()
    assert "".join(parser.parse("Text")) == "Text"


@pytest.fixture()
def parser():
    parser = Parser()
    pattern = r"^(?P<sharp>#+)\s+(?P<title>.*?)\n"

    def render(context, parser):
        content = f"{context['sharp']} <span>{context['title']}</span>"
        if len(context["sharp"]) <= 2:
            yield content
        else:
            cell = next(parser)
            if cell.match is None:
                yield "abc"
            else:
                yield "<div>" + content
                # yield "".join(cell.render(cell.context, parser))
                yield cell.result()  # same result above
                yield "</div>"

    parser.register(pattern, render)

    pattern = r"^(?P<prefix>`{3,})\n(?P<code>.*?)\n(?P=prefix)\n"

    def render(context, parser):
        content = f"<code>{context['code']}</code>"
        if len(context["prefix"]) <= 3:
            yield content
        else:
            yield "<pre>"
            yield from parser.parse(context["code"] + "\n")
            yield "</pre>"

    parser.register(pattern, render)

    return parser


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(["begin\n## title", "```\nprint(1)\n```", "end"])
    return source_simple


@pytest.fixture()
def source_complex():
    source_complex = "\n".join(
        ["begin\n### title", "````\n```\nprint(1)\n```\n````", "end"]
    )
    return source_complex


def test_register(parser):
    assert len(parser.patterns) == 2
    assert len(parser.renders) == 2
    keys = list(parser.patterns.keys())
    assert keys[0].startswith("render_")


def test_splitter_for_loop(parser, source_simple):
    splitter = parser.split(source_simple)
    for k, cell in enumerate(splitter):
        if k == 0:
            assert cell.source == "begin\n"
        elif k == 1:
            assert isinstance(cell.match, Match)
            assert cell.source == "## title\n"
        elif k == 2:
            assert isinstance(cell.match, Match)
            assert cell.source == "```\nprint(1)\n```\n"
        elif k == 3:
            assert cell.source == "end"


def test_parse(parser, source_complex):
    outputs = list(parser.parse(source_complex))
    answers = [
        "begin\n",
        "<div>### <span>title</span>",
        "<pre><code>print(1)</code></pre>",
        "</div>",
        "end",
    ]
    for output, answer in zip(outputs, answers):
        print(output, answer)
        assert output == answer


def test_result(parser, source_complex):
    splitter = parser.split(source_complex)
    next(splitter)
    next(splitter)
    cell = next(splitter)
    assert cell.result() == "<pre><code>print(1)</code></pre>"

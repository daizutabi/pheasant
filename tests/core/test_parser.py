from typing import Match

import pytest

from pheasant.core.parser import Parser, object_name


@pytest.fixture()
def parser():
    parser = Parser()
    pattern = r"^(?P<sharp>#+)\s+(?P<title>.*?)\n"

    def render(context, parser):
        content = f"{context['sharp']} <span>{context['title']}</span>"
        if len(context["sharp"]) <= 2:
            yield content
        else:
            splitted = parser.generator.send(all)
            if splitted["match"] is None:
                yield "abc"
            else:
                yield "<div>" + content
                yield from splitted["render"](splitted["context"], parser)
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
    splitter = parser.splitter(source_simple)
    next(splitter)
    for k, splitted in enumerate(splitter):
        if k == 0:
            assert splitted == "begin\n"
        elif k == 1:
            assert isinstance(splitted, Match)
            assert splitted.group() == "## title\n"
        elif k == 2:
            assert isinstance(splitted, Match)
            assert splitted.group() == "```\nprint(1)\n```\n"
        elif k == 3:
            assert splitted == "end"


def test_reap(parser, source_simple):
    splitter = parser.splitter(source_simple)
    next(splitter)
    for k, match in enumerate(splitter):
        if k == 1:
            cell = parser._reap(match)
            assert cell["name"] == object_name(cell["render"])
            context = cell["context"]
            assert cell["source"] == "## title\n"
            assert context["sharp"] == "##"
            assert context["title"] == "title"
        elif k == 2:
            cell = parser._reap(match)
            context = cell["context"]
            assert cell["source"] == "```\nprint(1)\n```\n"
            assert context["prefix"] == "```"
            assert context["code"] == "print(1)"


def test_splitter_send(parser, source_simple):
    splitter = parser.splitter(source_simple)
    next(splitter)
    assert splitter.send(None) == "begin\n"
    assert splitter.send(str) == "## title\n"
    assert splitter.send(dict)["context"]["code"] == "print(1)"
    assert splitter.send(dict)["source"] == "end"
    splitter = parser.splitter(source_simple)
    next(splitter)
    assert splitter.send(all)["source"] == "begin\n"
    assert splitter.send(all)["match"].group() == "## title\n"


def test_parse(parser, source_complex):
    outputs = list(parser.parse(source_complex))
    answers = [
        "begin\n",
        "<div>### <span>title</span>",
        "<pre>",
        "<code>print(1)</code>",
        "</pre>",
        "</div>",
        "end",
    ]
    for output, answer in zip(outputs, answers):
        assert output == answer

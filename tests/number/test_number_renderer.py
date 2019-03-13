import re
from typing import Pattern

import pytest

from pheasant.core.parser import Parser
from pheasant.number.renderer import HEADER_PATTERN, Number


@pytest.fixture()
def parser():
    parser = Parser()
    return parser


@pytest.fixture()
def number(parser):
    number = Number(parser, {"__dummy__": "test"})
    return number


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "begin\n# title\ntext a",
            "## section a\ntext b\n### subsection\n## section b\ntext c",
            "#Fig figure title a\n\nfigure content a1\nfigure content a2",
            "text d\n#Fig figure title b",
            "figure content b1\nfigure content b2\n\nend",
        ]
    )
    return source_simple


def test_complile_pattern():
    assert isinstance(re.compile(HEADER_PATTERN), Pattern)


def test_renderer(number):
    assert number.config["__dummy__"] == "test"
    assert "kind" in number.config
    assert number.config["header_template"] is not None
    assert number.page_index == 1
    assert number.header_kind == {
        "": "header",
        "fig": "figure",
        "tab": "table",
        "cod": "code",
        "fil": "file",
    }


def test_render_header(parser, number, source_simple):
    assert "Number_render_header" in parser.patterns
    assert "Number_render_labelheader" in parser.patterns
    assert parser.patterns["Number_render_header"].startswith(
        "(?P<Number_render_header>"
    )
    assert parser.renders["Number_render_header"] == number.render_header

    splitter = parser.splitter(source_simple)
    next(splitter)
    cell = splitter.send(all)
    assert cell["name"] is None
    assert cell["context"] == {}
    assert cell["source"] == "begin\n"
    cell = splitter.send(all)
    assert cell["name"] == "Number_render_header"
    assert cell["context"] == {"prefix": "#", "kind": "", "title": "title"}
    assert cell["source"] == "# title\n"

    for source in parser.parse(source_simple):
        print(source)

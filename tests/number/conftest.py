import pytest

from pheasant.core.parser import Parser
from pheasant.number.renderer import Anchor, Header


@pytest.fixture(scope="module")
def header():
    header = Header(config={"__dummy__": "test"})
    return header


@pytest.fixture(scope="module")
def anchor():
    anchor = Anchor()
    return anchor


@pytest.fixture()
def parser_header(header):
    parser = Parser()

    for pattern, render in header.renders.items():
        parser.register(pattern, render)

    return parser


@pytest.fixture()
def parser_anchor(anchor):
    parser = Parser()

    for pattern, render in anchor.renders.items():
        parser.register(pattern, render)

    return parser


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "# Title {#tag-a#}",
            "## Section A",
            "Text {#tag-b#}",
            "## Section B",
            "## Subsection C",
            "Text {#tag-a#}",
            "#Fig Figure A {#tag-b#}",
            "<div>Content A</div>"
        ]
    )
    return source_simple

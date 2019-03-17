import pytest

from pheasant.core.parser import Parser
from pheasant.number.renderer import Anchor, Header


@pytest.fixture(scope="module")
def header():
    header = Header(config={"__dummy__": "test"})
    header.config["header_template_file"] = "simple.jinja2"
    header.set_template("header")
    return header


@pytest.fixture(scope="module")
def anchor():
    anchor = Anchor()
    anchor.config["header_template_file"] = "simple.jinja2"
    anchor.set_template("header")
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
            "begin\n# title {#label-a#}\ntext a Figure {#label-b#}",
            "## section a\ntext b\n### subsection\n## section b\ntext c",
            "#Fig figure title a\n\nfigure content a1\nfigure content a2",
            "text d\n#Fig {#label-b#}figure title b Section {#label-a#}",
            "figure content b1\nfigure content b2\n\nend {#label-c#}",
        ]
    )
    return source_simple

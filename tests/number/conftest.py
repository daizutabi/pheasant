import pytest

from pheasant.core.parser import Parser
from pheasant.number.renderer import Linker, Number


@pytest.fixture(scope="module")
def number():
    number = Number({"__dummy__": "test"})
    number.config["header_template_file"] = "simple.jinja2"
    number.set_template("header")
    return number


@pytest.fixture(scope="module")
def linker():
    linker = Linker()
    linker.config["header_template_file"] = "simple.jinja2"
    linker.set_template("header")
    return linker


@pytest.fixture()
def parser_number(number):
    parser = Parser()

    for pattern, render in number.renders.items():
        parser.register(pattern, render)

    return parser


@pytest.fixture()
def parser_linker(linker):
    parser = Parser()

    for pattern, render in linker.renders.items():
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

import pytest

from pheasant.core.parser import Parser
from pheasant.number.renderer import Number


@pytest.fixture()
def parser():
    parser = Parser()
    return parser


@pytest.fixture()
def number(parser):
    number = Number(parser)
    number.config["header_template_file"] = "simple.jinja2"
    number.set_template("header")
    return number


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "begin\n# title {#label-a#}\ntext a {#label-b#}",
            "## section a\ntext b {#label-c#}\n### subsection\n## section b\ntext c",
            "#Fig figure title a\n\nfigure content a1\nfigure content a2\n",
            "text d{#label-a#}\n#Fig {#label-b#}figure title b",
            "figure content b1\nfigure content b2\n\nend",
        ]
    )
    return source_simple


def test_render_label(parser, number, source_simple):
    pass
    # number.reset_number_list()
    # output = "".join(parser.parse(source_simple))
    # number.save_label_context()
    # number.reset_number_list()
    # output = "".join(parser.parse(source_simple))
    # number.save_label_context()
    # number.reset_number_list()
    # output = "".join(parser.parse(source_simple))
    # print(output)
    print(source_simple)

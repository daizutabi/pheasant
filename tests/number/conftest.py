import pytest

from pheasant.core.parser import Parser
from pheasant.number.renderer import Number


@pytest.fixture()
def parser():
    parser = Parser()
    return parser


@pytest.fixture()
def number(parser):
    number = Number(parser, {"__dummy__": "test"})
    number.config["header_template_file"] = "simple.jinja2"
    number.set_template("header")
    return number

import pytest

from pheasant.core.parser import Parser
from pheasant.number.renderer import Number


@pytest.fixture()
def number():
    number = Number({"__dummy__": "test"})
    number.config["header_template_file"] = "simple.jinja2"
    number.set_template("header")
    return number


@pytest.fixture()
def parser(number):
    parser = Parser()

    for pattern, render in number.renders.items():
        parser.register(pattern, render)

    return parser

import pytest

from pheasant.code.renderer import Code
from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Header


@pytest.fixture()
def jupyter():
    jupyter = Jupyter()
    return jupyter


@pytest.fixture()
def header():
    header = Header()
    return header


@pytest.fixture()
def code():
    code = Code()
    return code


@pytest.fixture()
def parser(jupyter, header, code):
    parser = Parser()

    for pattern, render in jupyter.renders.items():
        parser.register(pattern, render)

    for pattern, render in code.renders.items():
        parser.register(pattern, render)

    for pattern, render in header.renders.items():
        parser.register(pattern, render)

    return parser

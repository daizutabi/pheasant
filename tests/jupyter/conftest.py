import pytest

from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter


@pytest.fixture()
def jupyter():
    jupyter = Jupyter()
    jupyter.execute("import pheasant.jupyter.display")
    return jupyter


@pytest.fixture()
def parser(jupyter):
    parser = Parser()

    for pattern, render in jupyter.renders.items():
        parser.register(pattern, render)

    return parser

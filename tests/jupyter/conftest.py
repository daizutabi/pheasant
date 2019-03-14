import pytest

from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter


@pytest.fixture()
def parser():
    parser = Parser()
    return parser


@pytest.fixture()
def jupyter(parser):
    jupyter = Jupyter(parser)
    return jupyter

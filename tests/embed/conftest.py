import pytest
import os

from pheasant.embed.renderer import Embed
from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Header


@pytest.fixture()
def jupyter():
    jupyter = Jupyter()
    directory = os.path.normpath(os.path.join(__file__, "../../jupyter/templates"))
    jupyter.set_template("fenced_code", directory)
    return jupyter


@pytest.fixture()
def header():
    header = Header()
    return header


@pytest.fixture()
def embed():
    embed = Embed()
    return embed


@pytest.fixture()
def parser(jupyter, header, embed):
    parser = Parser()
    jupyter.parser = parser
    header.parser = parser
    embed.parser = parser

    return parser

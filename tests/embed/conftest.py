import pytest
import os

from pheasant.embed.renderer import Embed
from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Header


@pytest.fixture()
def jupyter():
    jupyter = Jupyter()
    fenced_code_template_file = os.path.join(
        __file__, "../../jupyter/templates/fenced_code_test.jinja2"
    )
    fenced_code_template_file = os.path.abspath(fenced_code_template_file)
    jupyter._update("config", {"fenced_code_template_file": fenced_code_template_file})
    jupyter.set_template(["fenced_code"])
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
def parser(jupyter, header, code):
    parser = Parser()
    jupyter.parser = parser
    header.parser = parser
    code.parser = parser

    return parser

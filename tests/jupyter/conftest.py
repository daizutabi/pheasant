import os

import pytest

from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter


@pytest.fixture()
def jupyter():
    jupyter = Jupyter()

    fenced_code_template_file = os.path.join(
        __file__, "../templates/fenced_code_test.jinja2"
    )
    fenced_code_template_file = os.path.abspath(fenced_code_template_file)
    jupyter._update("config", {"fenced_code_template_file": fenced_code_template_file})
    jupyter.set_template(["fenced_code"])
    jupyter.execute("import pheasant.jupyter.display")
    return jupyter


@pytest.fixture()
def parser(jupyter):
    parser = Parser()

    for pattern, render in jupyter.renders.items():
        parser.register(pattern, render)

    return parser

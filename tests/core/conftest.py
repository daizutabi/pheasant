import os

import pytest

from pheasant.core.converter import Converter
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Anchor, Header


@pytest.fixture()
def jupyter():
    jupyter = Jupyter()

    fenced_code_template_file = os.path.join(
        __file__, "../../jupyter/templates/fenced_code_test.jinja2"
    )
    fenced_code_template_file = os.path.abspath(fenced_code_template_file)
    jupyter._update("config", {"fenced_code_template_file": fenced_code_template_file})
    jupyter.set_template(["fenced_code"])
    jupyter.execute("import pheasant.jupyter.display")
    return jupyter


@pytest.fixture()
def converter(jupyter):
    converter = Converter()
    converter.register("preprocess", [jupyter, Header()])
    converter.register("postprocess", Anchor())
    return converter

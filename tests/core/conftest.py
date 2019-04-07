import os

import pytest

from pheasant.core.converter import Converter
from pheasant.renderers.jupyter.jupyter import Jupyter
from pheasant.renderers.number.number import Anchor, Header


@pytest.fixture(scope="module")
def jupyter():
    jupyter = Jupyter()
    directory = os.path.normpath(
        os.path.join(__file__, "../../renderers/jupyter/templates")
    )
    jupyter.set_template("fenced_code", directory)
    return jupyter


@pytest.fixture(scope="module")
def converter(jupyter):
    converter = Converter()
    converter.register("preprocess", [jupyter, Header()])
    converter.register("postprocess", Anchor())
    return converter

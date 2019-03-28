import os

import pytest

from pheasant.core.converter import Converter
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Anchor, Header


@pytest.fixture(scope="module")
def jupyter():
    jupyter = Jupyter()
    directory = os.path.normpath(os.path.join(__file__, "../../jupyter/templates"))
    jupyter.set_template("fenced_code", directory)
    jupyter.execute("import pheasant.jupyter.display", "python")
    return jupyter


@pytest.fixture(scope="module")
def converter(jupyter):
    converter = Converter()
    converter.register("preprocess", [jupyter, Header()])
    converter.register("postprocess", Anchor())
    return converter

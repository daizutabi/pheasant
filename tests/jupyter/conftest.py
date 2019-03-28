import os

import pytest

from pheasant.jupyter.renderer import Jupyter


@pytest.fixture(scope="module")
def jupyter():
    jupyter = Jupyter()
    directory = os.path.normpath(os.path.join(__file__, "../templates"))
    jupyter.set_template("fenced_code", directory)
    jupyter.execute("import pheasant.jupyter.display", "python")
    return jupyter

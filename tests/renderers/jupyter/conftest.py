import os

import pytest

from pheasant.renderers.jupyter.jupyter import Jupyter


@pytest.fixture(scope="module")
def jupyter():
    jupyter = Jupyter()
    directory = os.path.normpath(os.path.join(__file__, "../templates"))
    jupyter.set_template("fenced_code", directory)
    jupyter.execute("import pheasant.renderers.jupyter.display", "python")
    return jupyter

import pytest

from pheasant.core.converter import Converter
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Anchor, Header


@pytest.fixture()
def converter():
    converter = Converter()
    converter.register("preprocess", [Jupyter(), Header()])
    converter.register("postprocess", Anchor())
    return converter

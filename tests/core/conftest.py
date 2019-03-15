import pytest

from pheasant.core.converter import Converter


@pytest.fixture()
def converter():
    converter = Converter()
    converter.register("preprocess", ["jupyter", "number"])
    converter.register("postprocess", ["linker"])
    return converter

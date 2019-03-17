import pytest

from pheasant.core.renderers import Renderers
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Number


@pytest.mark.parametrize("renderers_", [[Jupyter(), Number()], ("jupyter", "number")])
def test_renderers(renderers_):
    renderers = Renderers()
    renderers.register("markdown", renderers_)
    assert list(renderers.renderers.keys()) == ["markdown"]
    assert len(renderers.renderers["markdown"]) == 2


@pytest.fixture()
def renderers():
    renderers = Renderers()
    renderers.register("preprocess", ["jupyter", "number"])
    renderers.register("postprocess", "linker")
    return renderers


def test_converter_special_function(renderers):
    assert repr(renderers["preprocess"]) == "[<Jupyter#jupyter[2]>, <Number#number[1]>]"
    assert repr(renderers["preprocess", "jupyter"]) == "<Jupyter#jupyter[2]>"

    assert [repr(renderer) for renderer in renderers] == [
        "<Jupyter#jupyter[2]>",
        "<Number#number[1]>",
        "<Linker#linker[1]>",
    ]


# def test_converter_dict_function(renderers):
#     assert list(renderers.keys()) == ["preprocess", "postprocess"]
#     assert list(renderers.values()) == ["preprocess", "postprocess"]

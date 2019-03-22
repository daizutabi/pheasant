import pytest

from pheasant.core.renderers import Renderers
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Header, Anchor


def test_renderers():
    renderers = Renderers()
    renderers.register("markdown", [Jupyter(), Header()])
    assert list(renderers.renderers.keys()) == ["markdown"]
    assert len(renderers.renderers["markdown"]) == 2


@pytest.fixture()
def renderers():
    renderers = Renderers()
    renderers.register("preprocess", [Jupyter(), Header()])
    renderers.register("postprocess", [Anchor()])
    return renderers


def test_converter_special_function(renderers):
    assert repr(renderers["preprocess"]) == "[<Jupyter#jupyter[2]>, <Header#header[2]>]"
    assert repr(renderers["preprocess", "jupyter"]) == "<Jupyter#jupyter[2]>"

    assert [repr(renderer) for renderer in renderers] == [
        "<Jupyter#jupyter[2]>",
        "<Header#header[2]>",
        "<Anchor#anchor[1]>",
    ]


def test_converter_dict_function(renderers):
    assert list(renderers.keys()) == list(renderers.renderers.keys())
    assert list(renderers.values()) == list(renderers.renderers.values())
    assert list(renderers.items()) == list(renderers.renderers.items())

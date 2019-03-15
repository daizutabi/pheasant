import pytest

from pheasant.jupyter.client import execute
from pheasant.jupyter.renderer import Jupyter


@pytest.fixture()
def jupyter():
    jupyter = Jupyter()
    return jupyter


@pytest.fixture()
def render(jupyter):
    def render(code):
        context = dict(code=code, language="python")
        return "\n".join(jupyter.render_inline_code(context, None))

    return render


def test_import():
    code = "\n".join(
        [
            "import holoviews as hv",
            "from bokeh.plotting import figure",
            "from pheasant.jupyter.display import display",
        ]
    )
    assert execute(code) == []


def test_extra_resources(jupyter, render):
    jupyter.reset()
    extra = jupyter.config["extra_resources"]
    for key, value in extra.items():
        assert value == []
    code = "plot=figure()\nplot.circle([1,2],[3,5])\ndisplay(plot)"
    assert render(code).startswith("\n<script")
    assert extra["module"] == ["bokeh"]
    assert len(extra["extra_css"]) == 3
    assert len(extra["extra_javascript"]) == 4
    assert len(extra["extra_raw_css"]) == 0
    assert len(extra["extra_raw_javascript"]) == 0
    code = "curve=hv.Curve(((1,2),(3,4)))\ndisplay(curve)"
    assert render(code).startswith("<div")
    assert extra["module"] == ["bokeh", "holoviews"]
    assert len(extra["extra_css"]) == 5
    assert len(extra["extra_javascript"]) == 8
    assert len(extra["extra_raw_css"]) == 1
    assert len(extra["extra_raw_javascript"]) == 2

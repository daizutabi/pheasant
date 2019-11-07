import pytest
from bokeh.resources import CDN

from pheasant.renderers.jupyter.ipython import (altair_extra_resources,
                                                bokeh_extra_resources,
                                                holoviews_extra_resources,
                                                sympy_extra_resources)


@pytest.mark.parametrize(
    "key, values", [("extra_css", CDN.css_files), ("extra_javascript", CDN.js_files)]
)
def test_bokeh_extra_resources(key, values):
    resources = bokeh_extra_resources()
    assert resources[key] == values


@pytest.mark.parametrize(
    "index, host, name",
    [
        (0, "maxcdn.bootstrapcdn.com", "bootstrap.min.css"),
        (1, "code.jquery.com", "jquery-ui.css"),
    ],
)
def test_holoviews_extra_css(index, host, name):
    resources = holoviews_extra_resources()
    resources["extra_css"]
    split = resources["extra_css"][index].split("/")
    assert split[2] == host
    assert split[-1] == name


@pytest.mark.parametrize(
    "index, host, name",
    [
        (4, "code.jquery.com", None),
        (5, "code.jquery.com", "jquery-ui.min.js"),
        (6, "cdnjs.cloudflare.com", "require.min.js"),
        (7, "cdnjs.cloudflare.com", "underscore-min.js"),
    ],
)
def test_holoviews_extra_javascript(index, host, name):
    resources = holoviews_extra_resources()
    split = resources["extra_javascript"][index].split("/")
    assert split[2] == host
    if name:
        assert split[-1] == name


def test_holoviews_extra_raw_css():
    resources = holoviews_extra_resources()
    extra = resources["extra_raw_css"]
    assert len(extra) == 1
    assert extra[0].startswith("<style")


def test_holoviews_extra_raw_javascript():
    resources = holoviews_extra_resources()
    extra = resources["extra_raw_javascript"]
    assert len(extra) == 2
    assert extra[0].startswith("<script")


def test_altair_extra_resources():
    resources = altair_extra_resources()
    assert "extra_raw_css" in resources
    assert len(resources["extra_javascript"]) == 3


def test_sympy_extra_resources():
    resources = sympy_extra_resources()
    assert "extra_raw_javascript" in resources
    assert len(resources["extra_raw_javascript"]) == 1

import pytest
from bokeh.resources import CDN

from pheasant.renderers.jupyter.display import (bokeh_extra_resources,
                                                holoviews_extra_resources)


@pytest.mark.parametrize(
    "key, values", [("extra_css", CDN.css_files), ("extra_javascript", CDN.js_files)]
)
def test_bokeh_extra_resources(key, values):
    resources = bokeh_extra_resources()
    assert resources[key] == values


@pytest.mark.parametrize(
    "index, host, name",
    [
        (3, "maxcdn.bootstrapcdn.com", "bootstrap.min.css"),
        (4, "code.jquery.com", "jquery-ui.css"),
    ],
)
def test_holoviews_extra_css(index, host, name):
    resources = holoviews_extra_resources()
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

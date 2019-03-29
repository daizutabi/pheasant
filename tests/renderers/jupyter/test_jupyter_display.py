import altair as alt
import holoviews as hv
import matplotlib.pyplot as plt
import pandas as pd
import pytest
import sympy as sp
from bokeh.plotting import figure
from IPython.display import HTML, Latex

from pheasant.renderers.jupyter.display import (AltairHTML, BokehHTML,
                                                HoloviewsHTML,
                                                altair_extra_resources,
                                                base64image,
                                                bokeh_extra_resources, display,
                                                extra_resources,
                                                holoviews_extra_resources)


def test_display_matplotlib():
    fig = plt.figure(figsize=(2, 2))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2])
    display(fig)
    assert display(fig).startswith("![png](data:image/png;base64,iVBOR")
    assert isinstance(display(fig, output="html"), HTML)
    assert display(ax).startswith("![png](data:image/png;base64,iVBOR")


def test_display_dataframe():
    df = pd.DataFrame([[1, 2], [3, 4]], columns=list("ab"))
    assert isinstance(display(df, output="markdown"), HTML)
    assert isinstance(display(df, output="html"), HTML)


def test_display_bokeh():
    plot = figure(plot_width=250, plot_height=250)
    plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)

    html = display(plot)
    assert isinstance(html, BokehHTML)


def test_bokeh_extra_resources():
    resources = bokeh_extra_resources()
    assert "extra_css" in resources
    assert isinstance(resources["extra_css"], list)
    assert "extra_javascript" in resources
    assert isinstance(resources["extra_javascript"], list)


def test_display_holoviews():
    curve = hv.Curve(((1, 2), (3, 4)))
    html = display(curve)
    assert isinstance(html, HoloviewsHTML)


def test_holoviews_extra_resources():
    resources = holoviews_extra_resources()
    assert "extra_css" in resources
    assert isinstance(resources["extra_css"], list)
    assert "extra_raw_css" in resources
    assert isinstance(resources["extra_raw_css"], list)
    assert "extra_javascript" in resources
    assert isinstance(resources["extra_javascript"], list)
    assert "extra_raw_javascript" in resources
    assert isinstance(resources["extra_raw_javascript"], list)


def test_display_altair():
    source = pd.DataFrame(
        {
            "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
            "b": [14, 55, 43, 91, 81, 53, 19, 87, 52],
        }
    )
    chart = alt.Chart(source).mark_bar().encode(x="a", y="b")
    html = display(chart)
    assert isinstance(html, AltairHTML)


def test_altair_extra_resources():
    resources = altair_extra_resources()
    assert "extra_css" not in resources
    assert "extra_raw_css" in resources
    assert isinstance(resources["extra_raw_css"], list)
    assert "extra_javascript" in resources
    assert isinstance(resources["extra_javascript"], list)
    assert "extra_raw_javascript" not in resources


def test_extra_resources():
    extra = extra_resources(["bokeh", "holoviews", "altair"])
    extra == bokeh_extra_resources()
    assert "vega" in extra["extra_javascript"][0]
    assert len(extra["extra_css"]) == 5
    assert len(extra["extra_raw_css"]) == 2
    assert len(extra["extra_javascript"]) == 11
    assert len(extra["extra_raw_javascript"]) == 2


def test_display_sympy():
    x = sp.symbols("x")
    assert isinstance(display(3 * x ** 2), Latex)


def test_base64image():
    with pytest.raises(ValueError):
        base64image(b"000", "png", "unknown")


def test_misc():
    assert repr(BokehHTML()) == "bokeh"
    assert repr(HoloviewsHTML()) == "holoviews"
    assert repr(AltairHTML()) == "altair"
    assert display(1) == 1

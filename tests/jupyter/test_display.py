import holoviews as hv
import matplotlib.pyplot as plt
import pandas as pd
import pytest
import sympy as sp
from bokeh.plotting import figure

from pheasant.jupyter.display import base64image, display, holoviews_to_html


def test_display_text():
    a = 1
    assert display(a) == "1"
    assert display(a, output="html") == "<p>1</p>"

    a = "<a>"
    assert display(a) == "<a>"
    assert display(a, output="html") == "<p><a></p>"

    a = [1, "<a>"]
    assert display(a) == "[1, &#x27;&lt;a&gt;&#x27;]"
    assert display(a, output="html") == "<p>[1, '<a>']</p>"


def test_display_matplotlib():
    fig = plt.figure(figsize=(2, 2))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2])
    assert display(fig).startswith("![png](data:image/png;base64,iVBOR")
    assert display(fig, output="html").startswith(
        '<img alt="png" src="data:image/png;base64,iVBOR'
    )
    assert display(ax).startswith("![png](data:image/png;base64,iVBOR")


def test_display_dataframe():
    df = pd.DataFrame([[1, 2], [3, 4]], columns=list("ab"))
    assert display(df).startswith("<table")
    assert display(df, output="html").startswith("<table")


def test_display_bokeh():
    plot = figure(plot_width=250, plot_height=250)
    plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)

    html, resources = display(plot)
    assert html.strip().startswith('<script type="text/javascript">')

    html, resources = display(plot, output='html')
    assert html.strip().startswith('<script type="text/javascript">')


def test_display_holoviews():
    curve = hv.Curve(((1, 2), (3, 4)))
    html, resources = display(curve)
    assert html.startswith('<div style=\'display')

    png = holoviews_to_html(curve, fmt='png')
    assert png.startswith("![png](data:image/png;base64,iVBOR")


def test_display_sympy():
    x = sp.symbols('x')
    assert display(3 * x ** 2) == '3 x^{2}'


def test_object():
    class A:
        def __str__(self):
            return 'hello'
    a = A()
    assert display(a) == 'hello'


def test_base64image():
    with pytest.raises(ValueError):
        base64image(b'000', 'png', 'unknown')

import altair as alt
import holoviews as hv
import pandas as pd
from bokeh.plotting import figure

from pheasant.renderers.jupyter import ipython
from pheasant.renderers.jupyter.kernel import kernels


def test_ipython_pandas():
    df = pd.DataFrame([[1, 2], [3, 4]])
    assert ipython.pandas_dataframe_to_html(df).startswith("<table")
    s = pd.Series([1, 2])
    assert ipython.pandas_series_to_html(s).startswith("<table")


def test_ipython_bokeh():
    plot = figure(plot_width=250, plot_height=250)
    plot.circle([1, 2], [3, 4])
    html, meta = ipython.bokeh_to_html(plot)
    assert html.startswith("\n<script")
    assert meta == {"module": "bokeh"}


def test_ipython_holoviews():
    curve = hv.Curve(((1, 2), (3, 4)))
    html, meta = ipython.holoviews_to_html(curve)
    assert html.startswith("<div style")
    assert meta == {"module": "holoviews"}


def test_ipython_altair():
    source = pd.DataFrame(
        {
            "a": ["A", "B", "C", "D", "E", "F", "G", "H", "I"],
            "b": [30, 55, 43, 91, 81, 53, 19, 87, 52],
        }
    )
    chart = alt.Chart(source).mark_bar().encode(x="a", y="b")
    html, meta = ipython.altair_to_html(chart)
    assert html.startswith('<div id="pheasant-altair-')
    assert meta == {"module": "altair"}


# def test_ipython_sympy():
#     x = sympy.symbols("x")
#     html, meta = ipython.sympy_to_latex(3 * x ** 2)
#     assert html == "3 x^{2}"
#     assert meta == {"module": "sympy"}


def test_ipython_select_last_display_data():
    kernel = kernels["python"]
    kernel.execute("import matplotlib.pyplot as plt")
    code = "for k in range(2):\n print(1)\n plt.plot([1,2])\n plt.show()\n print(2)"
    outputs = kernel.execute(code)
    assert len(outputs) == 5
    ipython.select_last_display_data(outputs)
    assert len(outputs) == 2
    assert outputs[0]["type"] == "display_data"
    assert outputs[1]["text"] == "1\n2\n1\n2"

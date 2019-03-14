import pytest

from pheasant.jupyter.client import execute


def test_import():
    code = "\n".join(
        [
            "import holoviews as hv",
            "import matplotlib.pyplot as plt",
            "import pandas as pd",
            "import sympy as sp",
            "from bokeh.plotting import figure",
            "from pheasant.jupyter.display import display",
        ]
    )
    assert execute(code) == []


@pytest.mark.parametrize(
    "code,output", [(1, "1"), ("'a'", "'a'"), ("[1, 2, 3]", "[1, 2, 3]")]
)
def test_execute_display_text(code, output):
    outputs = execute(f"display({code})")
    assert outputs == [{"type": "execute_result", "data": {"text/plain": output}}]


def test_execute_display_matplotlib():
    code = "plt.plot([1, 2])"
    outputs_normal = execute(code)
    outputs_display = execute(f"display({code})")
    assert outputs_display[1] == outputs_normal[1]
    code = "fig=plt.figure()\nax=fig.add_subplot(1,1,1)\nax.plot([1,2])\nfig"
    outputs_normal = execute(code)
    code = code.replace("\nfig", "\ndisplay(fig)")
    outputs_display = execute(code)
    assert outputs_display[1] == outputs_display[1]
    text = outputs_display[0]["data"]["text/plain"]
    assert text.startswith("'![png](data:image/png;base64,i")
    code = code.replace("play(fig)", 'play(fig, output="html")')
    outputs_display = execute(code)
    assert outputs_display[0]["data"]["text/html"].startswith("<img")


def test_execute_display_dataframe():
    code = "df=pd.DataFrame([[1,2],[3,4]])\ndisplay(df)"
    outputs = execute(code)
    assert outputs[0]["data"]["text/html"].startswith("<table")


def test_execute_display_bokeh():
    code = "\n".join(
        [
            "plot=figure(plot_width=250,plot_height=250)",
            "plot.circle([1,2],[3,4])\ndisplay(plot)",
        ]
    )
    outputs = execute(code)
    assert outputs[0]["data"]["text/html"].startswith("\n<script")


def test_execute_display_holoviews():
    code = "curve = hv.Curve(((1, 2), (3, 4)))\ndisplay(curve)"
    outputs = execute(code)
    assert outputs[0]["data"]["text/html"].startswith("<div style")


def test_execute_display_sympy():
    code = "x = sp.symbols('x')\ndisplay(3*x**2)"
    outputs = execute(code)
    assert outputs[0]["data"]["text/latex"] == "3 x^{2}"
    code = "x = sp.symbols('x')\n3*x**2"
    outputs = execute(code)
    assert outputs[0]["data"]["text/plain"] == "3*x**2"

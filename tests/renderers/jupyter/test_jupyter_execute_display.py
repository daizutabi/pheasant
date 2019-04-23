import pytest

from pheasant.renderers.jupyter.kernel import kernels

kernel = kernels.get_kernel(kernels.get_kernel_name("python"))


def test_import():
    code = (
        "import holoviews as hv\n"
        "import matplotlib.pyplot as plt\n"
        "import pandas as pd\n"
        "import sympy as sp\n"
        "from bokeh.plotting import figure\n"
    )
    assert kernel.execute(code) == []


@pytest.mark.parametrize(
    "code,output", [("1", "1"), ("'a'", "'a'"), ("[1, 2, 3]", "[1, 2, 3]")]
)
def test_execute_display_text(code, output):
    outputs = kernel.execute(code)
    assert outputs == [
        {"type": "execute_result", "data": {"text/plain": output}, "metadata": {}}
    ]


def test_execute_display_dataframe():
    code = "df=pd.DataFrame([[1,2],[3,4]])\ndisplay(df)"
    outputs = kernel.execute(code)
    assert outputs[0]["data"]["text/html"].startswith("<table")


def test_execute_display_bokeh():
    code = (
        "plot=figure(plot_width=250,plot_height=250)\n"
        "plot.circle([1,2],[3,4])\ndisplay(plot)"
    )
    outputs = kernel.execute(code)
    assert outputs[0]["data"]["text/html"].startswith("\n<script")
    assert outputs[0]["metadata"]["text/html"] == {"module": "bokeh"}


def test_execute_display_holoviews():
    code = "curve = hv.Curve(((1, 2), (3, 4)))\ndisplay(curve)"
    outputs = kernel.execute(code)
    assert outputs[0]["data"]["text/html"].startswith("<div style")
    assert outputs[0]["metadata"]["text/html"] == {"module": "holoviews"}


def test_execute_display_sympy():
    code = "x = sp.symbols('x')\ndisplay(3*x**2)"
    outputs = kernel.execute(code)
    assert outputs[0]["data"]["text/latex"] == "3 x^{2}"
    code = "x = sp.symbols('x')\n3*x**2"
    outputs = kernel.execute(code)
    assert outputs[0]["data"]["text/plain"] == "3*x**2"
    outputs

from pheasant.renderers.jupyter.ipython import select_display_data
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


def test_select_display_data_text():
    outputs = kernel.execute("1")
    select_display_data(outputs)
    assert outputs == [
        {"type": "execute_result", "data": {"text/plain": "1"}, "metadata": {}}
    ]

    outputs = kernel.execute("print(1)")
    select_display_data(outputs)
    assert outputs == [{"type": "stream", "name": "stdout", "text": "1"}]

    outputs = kernel.execute("1/0")
    select_display_data(outputs)
    assert outputs[0]["type"] == "error"
    assert outputs[0]["ename"] == "ZeroDivisionError"
    assert outputs[0]["evalue"] == "division by zero"


def test_select_display_data_dataframe():
    code = "df=pd.DataFrame([[1,2],[3,4]])\ndf"
    outputs = kernel.execute(code)
    assert len(outputs[0]["data"]) == 2
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/html" in outputs[0]["data"]


def test_select_display_data_bokeh():
    code = (
        "plot=figure(plot_width=250,plot_height=250)\n"
        "plot.circle([1,2],[3,4])\nplot"
    )
    outputs = kernel.execute(code)
    assert len(outputs[0]) == 3
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/html" in outputs[0]["data"]


def test_select_display_data_holoviews():
    code = "curve = hv.Curve(((1, 2), (3, 4)))\ncurve"
    outputs = kernel.execute(code)
    assert len(outputs[0]) == 3
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/html" in outputs[0]["data"]


def test_select_display_data_sympy():
    code = "x = sp.symbols('x')\n3*x**2"
    outputs = kernel.execute(code)
    assert len(outputs[0]) == 3
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/latex" in outputs[0]["data"]

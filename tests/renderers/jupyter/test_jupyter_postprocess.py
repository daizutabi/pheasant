from pheasant.renderers.jupyter.client import execute
from pheasant.renderers.jupyter.display import select_display_data


def test_import():
    code = "\n".join(
        [
            "import holoviews as hv",
            "import matplotlib.pyplot as plt",
            "import pandas as pd",
            "import sympy as sp",
            "from bokeh.plotting import figure",
            "from pheasant.renderers.jupyter.display import display",
        ]
    )
    assert execute(code) == []


def test_select_display_data_text():
    outputs = execute("1")
    select_display_data(outputs)
    assert outputs == [{"type": "execute_result", "data": {"text/plain": "1"}}]

    outputs = execute("print(1)")
    select_display_data(outputs)
    assert outputs == [{"type": "stream", "name": "stdout", "text": "1"}]

    outputs = execute("1/0")
    select_display_data(outputs)
    assert outputs[0]["type"] == "error"
    assert outputs[0]["ename"] == "ZeroDivisionError"
    assert outputs[0]["evalue"] == "division by zero"


def test_select_display_data_text_with_display():
    outputs = execute("display(1)")
    select_display_data(outputs)
    assert outputs == [{"type": "execute_result", "data": {"text/plain": "1"}}]

    outputs = execute("display(print(1))")
    select_display_data(outputs)
    assert outputs == [{"type": "stream", "name": "stdout", "text": "1"}]

    outputs = execute("display(1/0)")
    select_display_data(outputs)
    assert outputs[0]["type"] == "error"
    assert outputs[0]["ename"] == "ZeroDivisionError"
    assert outputs[0]["evalue"] == "division by zero"


def test_select_display_data_matplotlib():
    code = "plt.plot([1, 2])"
    outputs_normal = execute(code)
    outputs_display = execute(f"display({code})")

    select_display_data(outputs_normal)
    select_display_data(outputs_display)
    assert outputs_display[1] == outputs_normal[1]

    code = "fig=plt.figure()\nax=fig.add_subplot(1,1,1)\nax.plot([1,2])\nfig"
    outputs_normal = execute(code)
    code = code.replace("\nfig", "\ndisplay(fig)")
    outputs_display = execute(code)
    select_display_data(outputs_normal)
    select_display_data(outputs_display)
    assert outputs_display[1] == outputs_display[1]
    text = outputs_display[0]["data"]["text/plain"]
    assert text.startswith("'![png](data:image/png;base64,i")
    code = code.replace("play(fig)", 'play(fig, output="html")')
    outputs_display = execute(code)
    select_display_data(outputs_display)
    assert outputs_display[0]["data"]["text/html"].startswith("<img")


def test_select_display_data_dataframe():
    code = "df=pd.DataFrame([[1,2],[3,4]])\ndf"
    outputs = execute(code)
    assert len(outputs[0]["data"]) == 2
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/html" in outputs[0]["data"]

    code = "df=pd.DataFrame([[1,2],[3,4]])\ndisplay(df)"
    outputs = execute(code)
    assert len(outputs[0]["data"]) == 2
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/html" in outputs[0]["data"]


def test_select_display_data_bokeh():
    code = "\n".join(
        [
            "plot=figure(plot_width=250,plot_height=250)",
            "plot.circle([1,2],[3,4])\ndisplay(plot)",
        ]
    )
    outputs = execute(code)
    assert len(outputs[0]) == 2
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/html" in outputs[0]["data"]


def test_select_display_data_holoviews():
    code = "curve = hv.Curve(((1, 2), (3, 4)))\ndisplay(curve)"
    outputs = execute(code)
    assert len(outputs[0]) == 2
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/html" in outputs[0]["data"]


def test_select_display_data_sympy():
    code = "x = sp.symbols('x')\ndisplay(3*x**2)"
    outputs = execute(code)
    assert len(outputs[0]) == 2
    select_display_data(outputs)
    assert len(outputs[0]["data"]) == 1
    assert "text/latex" in outputs[0]["data"]

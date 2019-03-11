from ast import literal_eval

from pheasant.jupyter.client import execute
from pheasant.jupyter.converter import initialize
from pheasant.jupyter.preprocess import preprocess_fenced_code


def test_initialize():
    initialize()
    assert execute("import matplotlib.pyplot as plt") == []


def test_preprocess_fenced_code():
    code = "{{plt.plot([1, 2])}}\n"
    output = preprocess_fenced_code(code)
    assert output == (
        "pheasant.jupyter.display.display(plt.plot" '([1, 2]), output="markdown")\n'
    )


def test_preprocess_fenced_code_with_asign():
    code = "a = {{plt.plot([1, 2])}}\n"
    output = preprocess_fenced_code(code)
    assert output == (
        "a = pheasant.jupyter.display.display(plt.plot" '([1, 2]), output="markdown")\n'
    )


def test_preprocess_fenced_code_html():
    code = "{{^plt.plot([1, 2])}}\n"
    output = preprocess_fenced_code(code)
    assert output == (
        "pheasant.jupyter.display.display(plt.plot" '([1, 2]), output="html")\n'
    )


def test_preprocess_fenced_code_with_semicolon():
    code = "{{plt.plot([1, 2]);plt.gcf()}}\n"
    output = preprocess_fenced_code(code)
    assert output == (
        "pheasant.jupyter.display.display(_pheasant_dummy, " 'output="markdown")\n'
    )
    outputs = execute("_pheasant_dummy")
    assert len(outputs) == 1
    data = outputs[0]["data"]
    assert data["text/plain"].startswith("<Figure size ")

    outputs = execute(output)
    assert len(outputs) == 1
    output = outputs[0]
    assert list(output["data"].keys()) == ["text/plain"]
    assert output["data"]["text/plain"].startswith("'![png]")


def test_run_preprocess_fenced_code_with_for_loop():
    code = (
        "a = []\nfor k in [1, 3]:\n"
        "    plt.plot([1, k])\n"
        "    a.append({{plt.gcf()}})\n"
    )
    output = preprocess_fenced_code(code)
    assert output.endswith('.display.display(plt.gcf(), output="markdown"))\n')
    outputs = execute(output)
    assert len(outputs) == 1
    data = outputs[0]["data"]
    assert data["text/plain"].startswith("<Figure size ")
    outputs = execute("a")
    assert len(outputs) == 1
    output = outputs[0]
    assert list(output["data"].keys()) == ["text/plain"]
    a = literal_eval(output["data"]["text/plain"])
    assert isinstance(a, list)

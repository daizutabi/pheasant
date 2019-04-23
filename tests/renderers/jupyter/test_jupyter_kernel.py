import pytest

from pheasant.renderers.jupyter.kernel import kernels


def test_kernel_names():
    assert "python" in kernels.kernel_names


@pytest.mark.parametrize("language", list(kernels.kernel_names.keys()))
def test_get_kernel_name(language):
    assert kernels.get_kernel_name(language) == kernels.kernel_names[language][0]


def test_execute():
    outputs = kernels.execute("print(1)")
    output = outputs[0]
    assert output["type"] == "stream"
    assert output["name"] == "stdout"
    assert output["text"] == "1"

    outputs = kernels.execute("print(1)\nprint(2)")
    assert outputs[0]["text"] == "1\n2"


def test_report():
    kernels.execute("2*3")
    assert "start" in kernels.report
    assert "end" in kernels.report
    assert "time" in kernels.report
    assert "total" in kernels.report


def test_no_kernel():
    assert kernels.get_kernel_name("abc") == ""

    with pytest.raises(ValueError):
        kernels.execute("abc", language="abc")


def test_stream_joinner():
    code = "import sys\nsys.stdout.write('1')\nsys.stdout.write('\x082')\n1"
    outputs = kernels.execute(code)
    assert outputs[0]["text"] == "2"
    assert outputs[1]["data"]["text/plain"] == "1"

    code = "sys.stdout.write('1')\nsys.stdout.write('2')\nsys.stderr.write('3')\n1"
    outputs = kernels.execute(code)
    assert outputs[0]["text"] == "12"
    assert outputs[1]["text"] == "3"


# def test_error_traceback():
#     outputs = kernels.execute("1/0")
#     assert "ZeroDivisionError" in outputs[0]["traceback"]

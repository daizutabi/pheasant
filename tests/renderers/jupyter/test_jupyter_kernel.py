import pytest

from pheasant.renderers.jupyter.kernel import kernels, output_hook_factory


def test_kernel_names():
    assert "python" in kernels.kernel_names


@pytest.mark.parametrize("language", list(kernels.kernel_names.keys()))
def test_get_kernel_name(language):
    assert kernels.get_kernel_name(language) == kernels.kernel_names[language][0]


def test_execute():
    outputs = kernels["python"].execute("print(1)")
    output = outputs[0]
    assert output["type"] == "stream"
    assert output["name"] == "stdout"
    assert output["text"] == "1"

    outputs = kernels["python"].execute("print(1)\nprint(2)")
    assert outputs[0]["text"] == "1\n2"


def test_report():
    kernel = kernels["python"]
    kernel.execute("2*3")
    assert "start" in kernel.report
    assert "end" in kernel.report
    assert "time" in kernel.report
    assert "total" in kernel.report


def test_no_kernel():
    assert kernels.get_kernel_name("abc") == ""


def test_stream_joinner():
    code = "import sys\nsys.stdout.write('1')\nsys.stdout.write('\x082')\n1"
    outputs = kernels["python"].execute(code)
    assert outputs[0]["text"] == "2"
    assert outputs[1]["data"]["text/plain"] == "1"

    code = "sys.stdout.write('1')\nsys.stdout.write('2')\nsys.stderr.write('3')\n1"
    outputs = kernels["python"].execute(code)
    assert outputs[0]["text"] == "12"
    assert outputs[1]["text"] == "3"


def test_kernel():
    kernel_name = kernels.get_kernel_name("python")
    kernel = kernels.get_kernel(kernel_name)
    kernel.execute("a=1")
    assert kernel.execute("a")[0]["data"]["text/plain"] == "1"
    kernel.restart()
    with pytest.raises(NameError):
        kernel.execute("a")

    assert kernel is kernels["python"]


def test_output_hook_factory():
    def func_stream(stream, data):
        assert stream == "stdout"
        assert data == "1\n"

    output_hook = output_hook_factory(func_stream)
    kernel = kernels["python"]
    kernel.execute("print(1)", output_hook=output_hook)

    def func_execute_result(stream, data):
        assert stream == "stdout"
        assert data == "123"

    output_hook = output_hook_factory(func_execute_result)
    kernel = kernels["python"]
    kernel.execute("123", output_hook=output_hook)

    def func_error(stream, data):
        assert stream == "stderr"
        assert "IndexError" in data

    output_hook = output_hook_factory(func_error)
    kernel = kernels["python"]
    kernel.execute("[][1]", output_hook=output_hook)


def test_inspect():
    kernel = kernels["python"]
    kernel.execute("?print")

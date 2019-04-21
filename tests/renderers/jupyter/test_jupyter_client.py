import pytest

from pheasant.renderers.jupyter.client import (execute, execution_report,
                                               find_kernel_names,
                                               get_kernel_name)


def test_find_kernel_names():
    kernel_names = find_kernel_names()
    assert "python" in kernel_names


kernel_names = find_kernel_names()
kernel_names_list = [kernel_names[language][0] for language in kernel_names]


@pytest.mark.parametrize("language", list(kernel_names.keys()))
def test_get_kernel_name(language):
    assert get_kernel_name(language) is not None


def test_execute():
    outputs = execute("print(1)")
    output = outputs[0]
    assert output["type"] == "stream"
    assert output["name"] == "stdout"
    assert output["text"] == "1"
    outputs = execute("print(1)\nprint(2)")
    assert outputs[0]["text"] == "1\n2"


def test_execution_report():
    execute("2*3")
    assert "start" in execution_report
    assert "end" in execution_report
    assert "time" in execution_report
    assert "page" in execution_report
    assert "life" in execution_report


def test_no_kernel():
    assert get_kernel_name("abc") is None

    with pytest.raises(ValueError):
        execute("abc", language="abc")


def test_stream_joinner():
    outputs = execute("import sys\nsys.stdout.write('1')\nsys.stdout.write('\x082')\n1")
    assert outputs[0]["text"] == "2"
    assert outputs[1]["data"]["text/plain"] == "1"

    source = "sys.stdout.write('1')\nsys.stdout.write('2')\nsys.stderr.write('3')\n1"
    outputs = execute(source)
    assert outputs[0]["text"] == "12"
    assert outputs[1]["text"] == "3"

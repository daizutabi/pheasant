import pytest

from pheasant.renderers.jupyter.client import (execute, execution_report,
                                     find_kernel_names, get_kernel_manager,
                                     get_kernel_name, kernel_managers)


def test_find_kernel_names():
    kernel_names = find_kernel_names()
    assert "python" in kernel_names


kernel_names = find_kernel_names()
kernel_names_list = [kernel_names[language][0] for language in kernel_names]


@pytest.mark.parametrize("language", list(kernel_names.keys()))
def test_get_kernel_name(language):
    assert get_kernel_name(language) is not None


@pytest.mark.parametrize("kernel_name", kernel_names_list)
def test_get_kernel_manager(kernel_name):
    kernel_manager = get_kernel_manager(kernel_name)
    assert kernel_name in kernel_managers
    assert kernel_manager.is_alive()
    assert kernel_manager is get_kernel_manager(kernel_name)


def test_execute():
    outputs = execute("print(1)")
    output = outputs[0]
    assert output["type"] == "stream"
    assert output["name"] == "stdout"
    assert output["text"] == "1"


def test_execution_report():
    execute("2*3")
    assert "start" in execution_report
    assert "end" in execution_report
    assert "elasped" in execution_report
    assert "total" in execution_report
    assert "execution_count" in execution_report
    assert "message" in execution_report


def test_no_kernel():
    assert get_kernel_name("abc") is None

    with pytest.raises(ValueError):
        execute("abc", language="abc")


def test_kernel_manager():
    km = get_kernel_manager("python")
    km.shutdown_kernel()
    assert not km.is_alive()
    km = get_kernel_manager("python")
    assert km.is_alive()

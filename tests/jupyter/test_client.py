import pytest

from pheasant.jupyter.client import (find_kernel_names, get_kernel_client,
                                     get_kernel_manager, kernel_clients,
                                     kernel_managers, run_cell)


def test_find_kernel_names():
    kernel_names = find_kernel_names()
    assert 'python' in kernel_names


kernel_names = find_kernel_names()
kernel_names_list = [kernel_names[language][0] for language in kernel_names]


@pytest.mark.parametrize('kernel_name', kernel_names_list)
def test_get_kernel_manager(kernel_name):
    kernel_manager = get_kernel_manager(kernel_name)
    assert kernel_name in kernel_managers
    assert kernel_manager.is_alive()
    assert kernel_manager is get_kernel_manager(kernel_name)


@pytest.mark.parametrize('kernel_name', kernel_names_list)
def test_get_kernel_client(kernel_name):
    kernel_client = get_kernel_client(kernel_name)
    assert kernel_name in kernel_clients
    assert kernel_client is get_kernel_client(kernel_name)


def test_run_cell():
    cell = run_cell('print(1)')
    output = cell['outputs'][0]
    assert output['output_type'] == 'stream'
    assert output['name'] == 'stdout'
    assert output['text'] == '1\n'

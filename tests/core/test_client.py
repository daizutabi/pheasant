import jupyter_client

import pytest
from pheasant.core.client import (find_kernel_names, get_kernel_client,
                                  get_kernel_manager, kernel_clients,
                                  kernel_managers)


def test_find_kernel_names():
    kernel_names = find_kernel_names()
    assert 'python' in kernel_names
    assert 'julia' in kernel_names


kernel_names = find_kernel_names()
kernel_names = [kernel_names[language][0] for language in kernel_names]


@pytest.mark.parametrize('kernel_name', kernel_names)
def test_get_kernel_magager(kernel_name):
    kernel_manager = get_kernel_manager(kernel_name)
    assert kernel_name in kernel_managers
    assert kernel_manager.is_alive()
    assert kernel_manager is get_kernel_manager(kernel_name)


@pytest.mark.parametrize('kernel_name', kernel_names)
def test_get_kernel_client(kernel_name):
    kernel_client = get_kernel_client(kernel_name)
    assert kernel_name in kernel_clients
    assert kernel_client is get_kernel_client(kernel_name)


def test_execute():
    pass
    # source = execute('python3', '1 + 1')
    # assert source[0]['code'] == '1 + 1'
    # assert source[1]['data']['text/plain'] == '2'


# test_get_kernel_magager()
#
# def get_client(kernel_name):
#     kernel_manager = get_kernel_manager(kernel_name)
#     if kernel_name in clients:
#         return clients[kernel_name]
#     else:
#         client = kernel_manager.client()
#         client.start_channels()
#         clients[kernel_name] = client
#         list(get_iopub_messages_until_idle(client))
#         return client
#
#
# def get_iopub_messages_until_idle(client):
#     while True:
#         content = client.get_iopub_msg()['content']
#         if 'execution_state' not in content:
#             yield content
#         elif content['execution_state'] == 'idle':
#             break
#
#
# def execute(kernel_name, code):
#     client = get_client(kernel_name)
#     client.execute(code)
#     return list(get_iopub_messages_until_idle(client))
#
#
# execute('doc', 'a=1')
# execute('doc', '%matplotlib inline\nimport matplotlib.pyplot as plt')
# execute('doc', 'plt.plot([1,2])')
#
#
# def

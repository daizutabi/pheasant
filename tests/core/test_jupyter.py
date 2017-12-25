import jupyter_client

from pheasant.core.jupyter import (clients, execute, get_client,
                                   get_kernel_manager, kernel_managers)

kernel_name = 'python3'


def test_kernelspec_find():
    kernel_specs = jupyter_client.kernelspec.find_kernel_specs()
    assert kernel_name in kernel_specs


def test_get_kernel_magager():
    kernel_manager = get_kernel_manager(kernel_name)
    assert kernel_name in kernel_managers
    assert kernel_manager.is_alive()
    assert kernel_manager is get_kernel_manager(kernel_name)


def test_get_client():
    client = get_client(kernel_name)
    assert kernel_name in clients
    assert client is get_client(kernel_name)


def test_execute():
    pass
    # execute(kernel_name, '1 + 1')


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

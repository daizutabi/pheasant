import jupyter_client

kernels_manager = {}
clients = {}


def get_kernel_manager(kernel_name):
    if kernel_name in kernels_manager:
        kernel_manager = kernels_manager[kernel_name]
    else:
        kernel_specs = jupyter_client.kernelspec.find_kernel_specs()
        if kernel_name not in kernel_specs:
            msg = f'Could not find kernel name: {kernel_name}'
            raise ValueError(msg)
        kernel_manager = jupyter_client.KernelManager(kernel_name=kernel_name)
        kernels_manager[kernel_name] = kernel_manager

    if not kernel_manager.is_alive():
        kernel_manager.start_kernel()

    return kernel_manager


def get_client(kernel_name):
    kernel_manager = get_kernel_manager(kernel_name)
    if kernel_name in clients:
        return clients[kernel_name]
    else:
        client = kernel_manager.client()
        client.start_channels()
        clients[kernel_name] = client
        list(get_iopub_messages_until_idle(client))
        return client


def get_iopub_messages_until_idle(client):
    while True:
        content = client.get_iopub_msg()['content']
        if 'execution_state' not in content:
            yield content
        elif content['execution_state'] == 'idle':
            break


def execute(kernel_name, code):
    client = get_client(kernel_name)
    client.execute(code)
    return list(get_iopub_messages_until_idle(client))


execute('doc', 'a=1')
execute('doc', '%matplotlib inline\nimport matplotlib.pyplot as plt')
execute('doc', 'plt.plot([1,2])')

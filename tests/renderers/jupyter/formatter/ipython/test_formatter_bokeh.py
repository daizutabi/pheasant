from pheasant.renderers.jupyter.client import execute, get_kernel_name

kernel_name = get_kernel_name('python')

execute('from IPython import get_ipython', kernel_name)
execute('ip = get_ipython()', kernel_name)
execute('ip.display_formatter.formatters', kernel_name)

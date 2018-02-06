import os

import nbformat
from jinja2 import FileSystemLoader

from .client import run_cell, select_kernel_name
from .config import config
from .markdown import convert as convert_markdown
from .notebook import convert as convert_notebook
from .notebook import new_exporter


def initialize():
    default_directory = os.path.join(os.path.dirname(__file__), 'templates')
    abspath = os.path.abspath(config['template_file'])
    template_directory, template_file = os.path.split(abspath)
    loader = FileSystemLoader([template_directory, default_directory])
    config['exporter'] = new_exporter(loader, template_file)

    kernel_name = select_kernel_name(language='python')
    config['python_kernel'] = kernel_name

    # TODO: run only if needed
    cell = nbformat.v4.new_code_cell('import sys, importlib, inspect')
    run_cell(cell, kernel_name)

    sys_path_insert()
    import_modules()
    init()


def convert(source):
    reload_modules()

    if not isinstance(source, str) or (os.path.exists(source) and
                                       source.endswith('.ipynb')):
        source = convert_notebook(source)
    else:
        source = convert_markdown(source)

    if config['output_format'] == 'notebook':
        source = str(source)

    return source


def sys_path_insert():
    for directory in config['package_dirs']:
        code = (f'if "{directory}" not in sys.path:\n'
                f'    sys.path.insert(0, "{directory}")')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])


def import_modules():
    for package in config['packages']:
        code = (f'module = importlib.import_module("{package}")\n'
                f'globals()["{package}"] = module')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])


def init():
    for code in config['init_codes']:
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])


def reload_modules():
    # TODO: check if reload is needed.
    for package in config['packages']:
        code = (f'module = importlib.import_module("{package}")\n'
                f'importlib.reload(module)')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])

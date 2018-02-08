import os

import nbformat
from jinja2 import FileSystemLoader

import pheasant

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

    abspath = os.path.abspath(config['inline_template_file'])
    inline_template_directory, inline_template_file = os.path.split(abspath)
    loader = FileSystemLoader([inline_template_directory, default_directory])
    config['inline_exporter'] = new_exporter(loader, inline_template_file)

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

    # from ..converters import get_source_file
    # source_file = get_source_file()
    # config['current_source_file'] = source_file
    # config['current_cell_source'] = []

    if not isinstance(source, str) or (os.path.exists(source) and
                                       source.endswith('.ipynb')):
        source = convert_notebook(source)
    else:
        source = convert_markdown(source)

    if config['output_format'] == 'notebook':
        source = str(source)

    # config['cell_source_cache'][source_file] = config['current_cell_source']

    return source


def sys_path_insert():
    pheasant_dir = os.path.abspath(os.path.join(pheasant.__file__, '../..'))
    pheasant_dir = pheasant_dir.replace('\\', '/')
    for directory in config['sys_paths'] + [pheasant_dir]:
        code = (f'if "{directory}" not in sys.path:\n'
                f'    sys.path.insert(0, "{directory}")')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])


def import_modules():
    for package in config['import_modules'] + ['pheasant', 'pandas']:
        code = (f'module = importlib.import_module("{package}")\n'
                f'globals()["{package}"] = module')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])


def init():
    for code in (config['init_codes'] +
                 ['pandas.options.display.max_colwidth = 0']):
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])


def reload_modules():
    for module in config['import_modules']:
        code = (f'module = importlib.import_module("{module}")\n'
                f'importlib.reload(module)')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell, config['python_kernel'])

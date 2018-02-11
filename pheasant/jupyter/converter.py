import os

import nbformat
from jinja2 import FileSystemLoader

import pheasant

from .client import run_cell
from .config import config
from .exporter import new_exporter
from .markdown import convert as convert_markdown

# from .notebook import convert as convert_notebook


def initialize():
    set_template()
    set_template('inline_')

    # TODO: run only if needed, only if the default language is Python.
    cell = nbformat.v4.new_code_cell('import sys, importlib, inspect')
    run_cell(cell)
    sys_path_insert()
    import_modules()
    run_init_codes()


def set_template(prefix=''):
    default_directory = os.path.join(os.path.dirname(__file__), 'templates')
    abspath = os.path.abspath(config[prefix + 'template_file'])
    template_directory, template_file = os.path.split(abspath)
    loader = FileSystemLoader([template_directory, default_directory])
    config[prefix + 'exporter'] = new_exporter(loader, template_file)


def convert(source) -> str:
    reload_modules()
    return convert_markdown(source)

    # if not isinstance(source, str) or (os.path.exists(source) and
    #                                    source.endswith('.ipynb')):
    #     source = convert_notebook(source)
    # else:
    #     source = convert_markdown(source)


def sys_path_insert():
    pheasant_dir = os.path.abspath(os.path.join(pheasant.__file__, '../..'))
    pheasant_dir = pheasant_dir.replace('\\', '/')
    for directory in config['sys_paths'] + [pheasant_dir]:
        code = (f'if "{directory}" not in sys.path:\n'
                f'    sys.path.insert(0, "{directory}")')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)


def import_modules():
    for package in config['import_modules'] + ['pheasant', 'pandas']:
        code = (f'module = importlib.import_module("{package}")\n'
                f'globals()["{package}"] = module')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)


def run_init_codes():
    for code in (config['init_codes'] +
                 ['pandas.options.display.max_colwidth = 0']):
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)


def reload_modules():
    for module in config['import_modules']:
        code = (f'module = importlib.import_module("{module}")\n'
                f'importlib.reload(module)')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)

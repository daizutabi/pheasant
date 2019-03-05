import os
from typing import Any, Dict, Generator, Optional

import nbformat
from jinja2 import Environment, FileSystemLoader
from nbconvert.filters import strip_ansi
from nbformat import NotebookNode

import pheasant
from pheasant.jupyter.client import run_cell, select_kernel_name
from pheasant.jupyter.config import config
from pheasant.jupyter.preprocess import (preprocess_fenced_code,
                                         preprocess_markdown)
from pheasant.jupyter.renderer import inline_render, render, run_and_render
from pheasant.markdown.splitter import fenced_code_splitter


def initialize() -> None:
    set_template()
    set_template('inline_')

    # TODO: run only if needed, only if the default language is Python.
    cell = nbformat.v4.new_code_cell('import sys, importlib, inspect')
    run_cell(cell)
    sys_path_insert()
    import_modules()
    run_init_codes()


def convert(source: str) -> str:
    """Convert markdown string into markdown with running results.

    Parameters
    ----------
    source : str
        Markdown source string.

    Returns
    -------
    results : str
        Markdown source with running results
    """
    reload_modules()

    config['run_counter'] = 0  # used in the cache module. MOVE!!
    return ''.join(cell_runner(source))


def cell_runner(source: str) -> Generator[str, None, None]:
    """Generate markdown string with outputs after running the source.

    Parameters
    ----------
    source : str
        Markdown source string.

    Yields
    ------
    str
        Markdown string.
    """
    for splitted in fenced_code_splitter(source):
        if isinstance(splitted, str):
            cmd = '<!-- break -->'
            if cmd in splitted:
                splitted = splitted[:splitted.index(cmd)]
                yield preprocess_markdown(splitted)
                break
            else:
                yield preprocess_markdown(splitted)
        else:
            language, source, options = splitted
            set_config(options)
            cell = new_code_cell(source, language=language, options=options)

            if 'inline' in options:
                cell.source = preprocess_fenced_code(cell.source)
                if 'hide' in options:
                    run_cell(cell)
                else:
                    yield run_and_render(cell, inline_render) + '\n\n'
            else:
                yield run_and_render(cell, render)


def new_code_cell(source: str, language: Optional[str] = None,
                  options: Optional[list] = None) -> NotebookNode:
    """Create a new code cell for evaluation.

    This function is used for any languages other than Python.
    """
    cell = nbformat.v4.new_code_cell(source)
    metadata: Dict[str, Any] = {}
    if language is not None:
        metadata['language'] = language
        kernel_name = select_kernel_name(language)
        metadata['kernel_name'] = kernel_name
    if options is not None:
        metadata['options'] = options
    cell.metadata['pheasant'] = metadata
    return cell


def set_config(options: list) -> None:
    sources = ['from pheasant.jupyter.config import config']
    for option in options:
        if '=' in option:
            keyword, value = option.split('=')
            if keyword in config:
                if isinstance(config[keyword], str):
                    source = f'config["{keyword}"] = "{value}"'
                else:
                    source = f'config["{keyword}"] = {value}'
                sources.append(source)
    if len(sources) > 1:
        source = '\n'.join(sources)
        cell = nbformat.v4.new_code_cell(source)
        run_cell(cell)


def set_template(prefix: str = '') -> None:
    default_directory = os.path.join(os.path.dirname(__file__), 'templates')
    abspath = os.path.abspath(config[prefix + 'template_file'])
    template_directory, template_file = os.path.split(abspath)
    loader = FileSystemLoader([template_directory, default_directory])
    env = Environment(loader=loader, autoescape=False)
    env.filters['strip_ansi'] = strip_ansi
    config[prefix + 'template'] = env.get_template(template_file)


def sys_path_insert() -> None:
    pheasant_dir = os.path.abspath(os.path.join(pheasant.__file__, '../..'))
    pheasant_dir = pheasant_dir.replace('\\', '/')
    for directory in config['sys_paths'] + [pheasant_dir]:
        code = (f'if "{directory}" not in sys.path:\n'
                f'    sys.path.insert(0, "{directory}")')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)


def import_modules() -> None:
    for package in config['import_modules'] + ['pheasant', 'pandas']:
        code = (f'module = importlib.import_module("{package}")\n'
                f'globals()["{package}"] = module')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)


def run_init_codes() -> None:
    for code in (config['init_codes']
                 + ['pandas.options.display.max_colwidth = 0']):
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)


def reload_modules() -> None:
    for module in config['import_modules']:
        code = (f'module = importlib.import_module("{module}")\n'
                f'importlib.reload(module)')
        cell = nbformat.v4.new_code_cell(code)
        run_cell(cell)

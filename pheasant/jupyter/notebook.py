import codecs
import re

import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

from .config import config


def convert(notebook, output_format=None):
    """
    Convert a notebook into a markdown string.

    Parameters
    ----------
    notebook : str or Notebook object
        If str, it is a filename.
    output_format : str, optional
        Output format. If `notebook`, a notebook object is returned
        before converting.

    Returns
    -------
    str or Notebook object
    """
    if isinstance(notebook, str):
        with codecs.open(notebook, 'r', 'utf8') as file:
            notebook = nbformat.read(file, as_version=config['format_version'])

    # For 'native' notebook, add language info to each code-cell.
    if 'kernelspec' in notebook.metadata:
        language = notebook.metadata.kernelspec.language
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                update_cell_metadata(cell, language)

    delete_dataframe_style(notebook)

    if (output_format or config['output_format']) == 'notebook':
        return notebook
    else:
        markdown, resources = config['exporter'].from_notebook_node(notebook)
        return drop_new_line_from_img_data(markdown)


def drop_new_line_from_img_data(markdown):
    re_compile = re.compile(r'<img .+?</img>', re.DOTALL)

    def replace(m):
        return m.group().replace('\n', '')

    return re_compile.sub(replace, markdown)


def delete_dataframe_style(notebook):
    re_compile = re.compile(r'<style scoped>.+?</style>',
                            re.DOTALL | re.MULTILINE)

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            for output in cell.outputs:
                if 'data' in output and 'text/html' in output.data:
                    html = re_compile.sub('', output.data['text/html'])
                    output.data['text/html'] = html


def new_exporter(loader=None, template_file=None):
    c = Config({'NbConvertBase': {
        'display_data_priority': ['application/vnd.jupyter.widget-state+json',
                                  'application/vnd.jupyter.widget-view+json',
                                  'application/javascript',
                                  'text/html',
                                  'text/markdown',
                                  'image/svg+xml',
                                  'text/latex',
                                  'image/png',
                                  'image/jpeg',
                                  'text/plain']
    }})

    exporter = MarkdownExporter(config=c,
                                extra_loaders=[loader] if loader else None)
    exporter.template_file = template_file
    return exporter


def update_cell_metadata(cell, language, option=None):
    """
    Add pheasant original metadata. This metadata is used when notebook
    is exported to markdown.
    """
    # For notebook
    if option is None and 'pheasant' in cell.metadata:
        option = cell.metadata['pheasant']

    if option:
        if isinstance(option, str):
            options = [option.strip() for option in option.split(',')]
        else:
            options = option
    else:
        options = []

    pheasant_metadata = {'options': options, 'language': language}
    cell.metadata['pheasant'] = pheasant_metadata
    return cell


def execute(notebook, timeout=None):
    """
    Execute a notebook
    """
    timeout = timeout or config['timeout']
    ep = ExecutePreprocessor(timeout=timeout)
    ep.preprocess(notebook, {})

import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

from pheasant.config import config

config = config['jupyter']


def convert(notebook, output='markdown'):
    """
    Convert a notebook into a markdown string.

    Parameters
    ----------
    notebook : str or Notebook object
        If str, it is a filename.
    output : str
        Output format. If `notebook`, a notebook object is returned
        before converting.

    Returns
    -------
    str or Notebook object
    """
    exporter = new_exporter()
    if isinstance(notebook, str):
        with open(notebook) as f:
            notebook = nbformat.read(f, as_version=config['format_version'])

    # For 'native' notebook, add language info to each code-cell.
    if 'kernelspec' in notebook.metadata:
        language = notebook.metadata.kernelspec.language
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                update_cell_metadata(cell, language)

    if output == 'notebook':
        return notebook
    else:
        markdown, resources = exporter.from_notebook_node(notebook)
        return markdown


def new_exporter():
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

    exporter = MarkdownExporter(config=c)
    exporter.template_file = config['template']
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


def execute(notebook, timeout=600):
    """
    Execute a notebook
    """
    timeout = config['timeout']
    ep = ExecutePreprocessor(timeout=timeout)
    ep.preprocess(notebook, {})

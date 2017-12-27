import logging

import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

from pheasant.config import config

config = config['jupyter']

log = logging.getLogger(__name__)


def convert(notebook, output='markdown'):
    """
    Convert a notebook into markdown string.

    Parameters
    ----------
    notebook : str or Notebook object
        if str, it is a filename
    output : str
        Output format. If `notebook`, notebook object is returned
        before converting. This is useful for debugging.

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
    ep.preprocess(notebook, {})  # Execute
    # ep.preprocess_cell(cell, resources, index)

# def convert(notebook):
#     """
#     Convert a markdown with valid links and figures.
#     """
#     markdown, resources = export(notebook)
#     return markdown

    # outputs = resources['outputs']
    #
    # re_link = re.compile(r'\[.*?\]\((.+?)\)')
    #
    # def replace(m):
    #     src = m.group(1)
    #     src_path = os.path.join(notebook_dir, src)
    #     if src.endswith('.ipynb'):
    #         dst = get_page_path(src)
    #     elif os.path.exists(src_path):
    #         dst = src
    #         dst_path = os.path.join(doc_dir, dst)
    #         shutil.copy2(src_path, dst_path)
    #     elif src in outputs:
    #         dst = name + src
    #         dst_path = os.path.join(doc_dir, dst)
    #         with open(dst_path, 'wb') as file:
    #             file.write(outputs[src])
    #
    #     return m.group().replace(src, dst)
    #
    # return re_link.sub(replace, markdown)
    #
    # return markdown
    #
    #
# def convert_link(path, source, outputs):
#     notebook_path = get_notebook_abspath(path)
#     notebook_dir = os.path.dirname(notebook_path)
#     doc_path = get_doc_abspath(path)
#     doc_dir, name = os.path.split(doc_path)
#     name = os.path.splitext(name)[0] + '_'
#
#     def replace(m):
#         src = m.group(1)
#         src_path = os.path.join(notebook_dir, src)
#         if src.endswith('.ipynb'):
#             dst = get_page_path(src)
#         elif os.path.exists(src_path):
#             dst = src
#             dst_path = os.path.join(doc_dir, dst)
#             shutil.copy2(src_path, dst_path)
#         elif src in outputs:
#             dst = name + src
#             dst_path = os.path.join(doc_dir, dst)
#             with open(dst_path, 'wb') as file:
#                 file.write(outputs[src])
#
#         return m.group().replace(src, dst)
#
#     return re_link.sub(replace, source)

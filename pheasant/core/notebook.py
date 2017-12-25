import logging
import re

import nbformat
from nbconvert import MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor
from traitlets.config import Config

from pheasant.config import config

config = config['notebook']

log = logging.getLogger(__name__)


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


def execute(notebook, timeout=600, kernel='python3'):
    """
    Execute a notebook
    """
    timeout = config['timeout']
    kernel = config['kernel']
    ep = ExecutePreprocessor(timeout=timeout, kernel_name=kernel)
    ep.preprocess(notebook, {})  # Execute
    # ep.preprocess_cell(cell, resources, index)


def export(notebook):
    """
    Export markdown and resources from a notebook
    """
    exporter = new_exporter()
    if isinstance(notebook, str):
        with open(path) as f:
            notebook = nbformat.read(f, as_version=config['format_version'])

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            if 'pheasant' not in cell.metadata:
                cell.metadata['pheasant'] = []
            elif not isinstance(cell.metadata['pheasant'], list):
                cell.metadata['pheasant'] = [cell.metadata['pheasant']]

    markdown, resources = exporter.from_notebook_node(notebook)
    return markdown, resources


def convert(notebook):
    """
    Convert a markdown with valid links and figures.
    """
    markdown, resources = export(notebook)
    return markdown

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

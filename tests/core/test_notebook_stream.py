import os

import nbformat
import pytest

from pheasant.core.notebook import execute, export
from pheasant.utils import read


@pytest.fixture
def stream_input():
    return read(__file__, 'mkdocs/docs/notebook_stream_input.ipynb')


@pytest.fixture
def stream_output():
    return read(__file__, 'mkdocs/docs/markdown_stream_output.md')


def test_new_notebook_stream(stream_input, stream_output):
    notebook = stream_input
    cell = notebook.cells[0]
    assert cell.cell_type == 'markdown'
    assert cell.source == '# Title\n\nText1'
    cell = notebook.cells[1]
    assert cell.cell_type == 'code'
    assert cell.source == 'def func(x):\n    return 2 * x'
    cell = notebook.cells[2]
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text2'
    cell = notebook.cells[3]
    assert cell.cell_type == 'code'
    assert cell.source == 'func(1)'
    cell = notebook.cells[4]
    assert cell.cell_type == 'code'
    assert cell.source == 'func(2)'
    assert cell['metadata']['pheasant'] == 'hide-input'
    cell = notebook.cells[5]
    assert cell.cell_type == 'code'
    assert cell.source == 'func(3)'
    assert cell['metadata']['pheasant'] == 'hide-output'
    cell = notebook.cells[6]
    assert cell.cell_type == 'code'
    assert cell.source == 'func(4)'
    assert cell['metadata']['pheasant'] == ['hide']
    cell = notebook.cells[7]
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text3'


def test_execute_and_export_stream(stream_input, stream_output):
    notebook = stream_input
    execute(notebook)
    markdown, resources = export(notebook)
    for markdown_line, stream_output_line in zip(markdown.split('\n'),
                                                 stream_output.split('\n')):
        assert markdown_line == stream_output_line

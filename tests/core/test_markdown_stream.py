import pytest

from pheasant.core.markdown import fenced_code_splitter, new_notebook
from pheasant.core.notebook import execute, export
from pheasant.utils import read


@pytest.fixture
def stream_input():
    return read(__file__, 'mkdocs/docs/markdown_stream_input.md')


@pytest.fixture
def stream_output():
    return read(__file__, 'mkdocs/docs/markdown_stream_output.md')


def test_fenced_code_splitter(stream_input):
    nodes = fenced_code_splitter(stream_input, 'jupyter')
    assert next(nodes) == '# Title\n\nText1'
    assert next(nodes) == ('def func(x):\n    return 2 * x', '')
    assert next(nodes) == 'Text2'
    assert next(nodes) == ('func(1)', '')
    assert next(nodes) == ('func(2)', 'hide-input')
    assert next(nodes) == ('func(3)', 'hide-output')
    assert next(nodes) == ('func(4)', 'hide')
    assert next(nodes) == 'Text3'


def test_new_notebook_stream(stream_input):
    notebook = new_notebook(stream_input, language='python')
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
    assert cell['metadata']['pheasant'] == []
    cell = notebook.cells[4]
    assert cell.cell_type == 'code'
    assert cell.source == 'func(2)'
    assert cell['metadata']['pheasant'] == ['hide-input']
    cell = notebook.cells[5]
    assert cell.cell_type == 'code'
    assert cell.source == 'func(3)'
    assert cell['metadata']['pheasant'] == ['hide-output']
    cell = notebook.cells[6]
    assert cell.cell_type == 'code'
    assert cell.source == 'func(4)'
    assert cell['metadata']['pheasant'] == ['hide']
    cell = notebook.cells[7]
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text3'


def test_execute_and_export_stream(stream_input, stream_output):
    language = 'python'
    notebook = new_notebook(stream_input, language=language)
    execute(notebook)
    markdown, resources = export(notebook)
    for markdown_line, stream_output_line in zip(markdown.split('\n'),
                                                 stream_output.split('\n')):
        assert markdown_line == stream_output_line

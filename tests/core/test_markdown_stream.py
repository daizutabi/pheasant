import pytest

from pheasant.core.markdown import fenced_code_splitter, cell_generator
from pheasant.core.notebook import execute, export
from pheasant.utils import read


@pytest.fixture
def stream_input():
    return read(__file__, 'mkdocs/docs/markdown_stream_input.md')


@pytest.fixture
def stream_output():
    return read(__file__, 'mkdocs/docs/markdown_stream_output.md')


def test_fenced_code_splitter(stream_input):
    nodes = fenced_code_splitter(stream_input)
    assert next(nodes) == '# Title\n\nText1'
    assert next(nodes) == ('python', 'def func(x):\n    return 2 * x', '')
    assert next(nodes) == 'Text2'
    assert next(nodes) == ('python', 'func(1)', '')
    assert next(nodes) == ('python', 'func(2)', 'hide-input')
    assert next(nodes) == ('python', 'func(3)', 'hide-output')
    assert next(nodes) == ('python', 'func(4)', 'hide')
    assert next(nodes) == 'Text3'


def test_new_notebook_stream(stream_input):
    cells = cell_generator(stream_input)
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == '# Title\n\nText1'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'def func(x):\n    return 2 * x'
    assert cell['metadata']['pheasant']['language'] == 'python'
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text2'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(1)'
    assert cell['metadata']['pheasant']['options'] == []
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(2)'
    assert cell['metadata']['pheasant']['options'] == ['hide-input']
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(3)'
    assert cell['metadata']['pheasant']['options'] == ['hide-output']
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(4)'
    assert cell['metadata']['pheasant']['options'] == ['hide']
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text3'


def test_execute_and_export_stream(stream_input, stream_output):
    language = 'python'
    # notebook = new_notebook(stream_input, language=language)
    # execute(notebook)
    # markdown, resources = export(notebook)
    # for markdown_line, stream_output_line in zip(markdown.split('\n'),
    #                                              stream_output.split('\n')):
    #     assert markdown_line == stream_output_line

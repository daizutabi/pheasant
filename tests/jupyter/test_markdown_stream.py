import pytest

from pheasant.jupyter.converter import initialize
from pheasant.jupyter.markdown import (cell_generator, cell_runner, convert,
                                       fenced_code_splitter)
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


def test_cell_generator_stream(stream_input):
    cells = cell_generator(stream_input)
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == '# Title\n\nText1'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'def func(x):\n    return 2 * x'
    assert cell.metadata.pheasant.language == 'python'
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text2'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(1)'
    assert cell.metadata.pheasant.options == []
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(2)'
    assert cell.metadata.pheasant.options == ['hide-input']
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(3)'
    assert cell.metadata.pheasant.options == ['hide-output']
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(4)'
    assert cell.metadata.pheasant.options == ['hide']
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text3'


def test_cell_runner_stream(stream_input):
    cells = cell_runner(stream_input)
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == '# Title\n\nText1'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'def func(x):\n    return 2 * x'
    assert cell.metadata.pheasant.language == 'python'
    assert cell.outputs == []
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text2'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(1)'
    assert cell.metadata.pheasant.options == []
    assert cell.outputs[0]['data']['text/plain'] == '2'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(2)'
    assert cell.metadata.pheasant.options == ['hide-input']
    assert cell.outputs[0]['data']['text/plain'] == '4'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(3)'
    assert cell.metadata.pheasant.options == ['hide-output']
    assert cell.outputs[0]['data']['text/plain'] == '6'
    cell = next(cells)
    assert cell.cell_type == 'code'
    assert cell.source == 'func(4)'
    assert cell.metadata.pheasant.options == ['hide']
    assert cell.outputs[0]['data']['text/plain'] == '8'
    cell = next(cells)
    assert cell.cell_type == 'markdown'
    assert cell.source == 'Text3'


@pytest.mark.parametrize('output_format', ['notebook', 'markdown', None])
def test_execute_and_export_stream(stream_input, stream_output, output_format):
    initialize()
    output = convert(stream_input, output_format=output_format)
    if output_format != 'notebook':
        assert isinstance(output, str)
        lines = zip(output.split('\n'), stream_output.split('\n'))
        for markdown_line, stream_output_line in lines:
            assert markdown_line == stream_output_line
    else:
        assert hasattr(output, 'cells')

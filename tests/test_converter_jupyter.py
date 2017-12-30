import os

import pytest
from pheasant import jupyter
from pheasant.converters import (convert, get_converter_name, get_converters,
                                 set_converters, update_config)
from pheasant.utils import read


@pytest.fixture
def root():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(root, 'resources/mkdocs/docs'))
    return root


@pytest.fixture
def stream_output():
    return read(__file__, 'mkdocs/docs/markdown_stream_output.md')


def test_converters():
    set_converters([jupyter])
    assert get_converters() == [jupyter]


def test_get_converter_name():
    assert get_converter_name(jupyter) == 'jupyter'


def test_jupyter_config():
    assert jupyter.config['format_version'] == 4
    assert jupyter.config['output_format'] == 'markdown'
    assert jupyter.config['kernel_name'] == {'python': 'python3'}
    assert 'configured' not in jupyter.config


def test_jupyter_update_config():
    config = {'jupyter': {'output_format': 'notebook',
                          'kernel_name': {'julia': 'julia'}}}
    update_config(jupyter, config)
    assert jupyter.config['output_format'] == 'notebook'
    assert jupyter.config['kernel_name'] == {'python': 'python3',
                                             'julia': 'julia'}
    assert jupyter.config['configured'] is True
    config = {'jupyter': {'output_format': 'markdown'}}
    update_config(jupyter, config)
    assert jupyter.config['output_format'] == 'notebook'
    jupyter.config['configured'] = False
    update_config(jupyter, config)
    assert jupyter.config['output_format'] == 'markdown'
    jupyter.config['configured'] = False


paths = ['markdown_stream_input.md', 'notebook_stream_input.ipynb']


@pytest.mark.parametrize('output_format', ['notebook', 'markdown'])
@pytest.mark.parametrize('path', paths)
def test_convert(root, stream_output, output_format, path):
    config = {'jupyter': {'output_format': output_format}}
    source = convert(os.path.join(root, path), config)
    assert jupyter.config['output_format'] == output_format
    jupyter.config['configured'] = False

    if output_format == 'markdown':
        assert source == stream_output
    elif output_format == 'notebook':
        assert source.startswith('{')

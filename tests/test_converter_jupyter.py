import os

import pytest

from pheasant import jupyter
from pheasant.converters import (get_converter_name, get_converters,
                                 set_converters, update_converter_config)
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
    assert jupyter.config['kernel_name'] == {'python': 'python3'}
    assert 'configured' not in jupyter.config


def test_jupyter_update_converter_config():
    config = {'jupyter': {'kernel_name': {'julia': 'julia'}}}
    update_converter_config(jupyter, config)
    assert jupyter.config['kernel_name'] == {'python': 'python3',
                                             'julia': 'julia'}
    assert jupyter.config['configured'] is True

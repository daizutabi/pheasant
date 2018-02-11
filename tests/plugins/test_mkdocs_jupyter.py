import os

import pytest
from mkdocs.config import load_config

from pheasant import jupyter
from pheasant.converters import set_converters, get_converters
from pheasant.plugins.mkdocs import PheasantPlugin
from pheasant.utils import read


@pytest.fixture(scope='function')
def plugin():
    return PheasantPlugin()


def test_converters():
    set_converters([jupyter])
    assert get_converters() == [jupyter]


@pytest.fixture
def stream_input():
    return read(__file__, 'mkdocs/docs/markdown_stream_input.md')


@pytest.fixture
def stream_output():
    return read(__file__, 'mkdocs/docs/markdown_stream_output.md')


@pytest.fixture
def root():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(root, '../resources/mkdocs'))
    return root


@pytest.fixture(scope='function')
def config(root):
    curdir = os.curdir
    os.chdir(root)
    yield load_config()
    os.chdir(curdir)


@pytest.fixture(scope='function')
def jupyter_config(config):
    return config['plugins']['pheasant'].config['jupyter']


def test_config(jupyter_config):
    assert isinstance(jupyter_config, dict)


class Page:
    def __init__(self, abs_input_path):
        self.abs_input_path = abs_input_path
        self.input_path = abs_input_path  # for log


paths = ['docs/markdown_stream_input.md', 'docs/notebook_stream_input.ipynb']


@pytest.mark.parametrize('path', paths)
def test_on_page_read_source(plugin, config, jupyter_config, root,
                             stream_output, path):
    page = Page(os.path.join(root, path))
    source = plugin.on_page_read_source(None, page, config)
    jupyter.config['configured'] = False

    assert source.strip() == stream_output.strip()

import os

import pytest
from mkdocs import nav
from mkdocs.config import load_config

from pheasant import number
from pheasant.converters import get_converters, set_converters, convert
from pheasant.plugins.mkdocs import PheasantPlugin
from pheasant.utils import read


def test_converters():
    set_converters([number])
    assert get_converters() == [number]


@pytest.fixture
def root():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(root, '../resources/mkdocs'))
    return root


@pytest.fixture
def config(root):
    curdir = os.curdir
    os.chdir(root)
    yield load_config()
    os.chdir(curdir)


@pytest.fixture
def site_navigation(config):
    return nav.SiteNavigation(config)


@pytest.fixture
def number_config(config):
    return config['plugins']['pheasant'].config['number']


@pytest.fixture
def plugin():
    return PheasantPlugin()


def test_config(number_config):
    assert isinstance(number_config, dict)


def test_pages(site_navigation, config):
    for k, page in enumerate(site_navigation.walk_pages()):
        source = convert(page.abs_input_path, config)
        assert number.config['pages'][k] == page.abs_input_path

    # class Page:
    #     def __init__(self, abs_input_path):
    #         self.abs_input_path = abs_input_path
    #
    #
    # paths = ['docs/markdown_stream_input.md', 'docs/notebook_stream_input.ipynb']
    #
    #
    # @pytest.mark.parametrize('output_format', ['notebook', 'markdown', 'html'])
    # @pytest.mark.parametrize('path', paths)
    # def test_on_page_read_source(plugin, config, jupyter_config, root,
    #                              stream_output, output_format, path):
    #     page = Page(os.path.join(root, path))
    #     jupyter_config['output_format'] = output_format
    #     source = plugin.on_page_read_source(None, page, config)
    #     jupyter._configured = False
    #
    #     if output_format == 'html':
    #         assert source == stream_output
    #     elif output_format == 'markdown':
    #         assert source.startswith('<pre># Title')
    #     elif output_format == 'notebook':
    #         assert source.startswith('<pre>{')

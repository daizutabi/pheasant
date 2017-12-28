import os

import pytest
from mkdocs.config import load_config
from pheasant.jupyter.config import config as pheasant_config
from pheasant.plugins.mkdocs import PheasantPlugin
from pheasant.utils import read


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
def plugin():
    return PheasantPlugin()


def test_on_config(plugin, config):
    plugin_config = config['plugins']['pheasant'].config['jupyter']
    assert plugin_config['output_format'] == 'html'
    assert plugin_config['kernel_name'] == {'python': 'python3'}
    assert pheasant_config['kernel_name'] == {'python': 'python3'}
    plugin_config['output_format'] = 'markdown'
    plugin_config['template_file'] = 'template.jinja2'
    plugin_config['kernel_name'] = {'julia': 'julia'}
    template = pheasant_config['template_file']
    plugin.on_config(config)
    assert pheasant_config['output_format'] == 'markdown'
    assert pheasant_config['template_file'] == 'template.jinja2'
    assert pheasant_config['kernel_name'] == {'julia': 'julia',
                                              'python': 'python3'}
    pheasant_config['template_file'] = template


class Page:
    def __init__(self, abs_input_path):
        self.abs_input_path = abs_input_path


paths = ['docs/markdown_stream_input.md', 'docs/notebook_stream_input.ipynb']


@pytest.mark.parametrize('output_format', ['notebook', 'markdown', 'html'])
@pytest.mark.parametrize('path', paths)
def test_on_page_read_source(plugin, config, root, stream_output,
                             output_format, path):
    page = Page(os.path.join(root, path))
    pheasant_config['output_format'] = output_format
    source = plugin.on_page_read_source(None, page, config)

    if output_format != 'notebook':
        assert source == stream_output
    else:
        assert source.startswith('<h1>DEBUG MODE</h1><pre>{')

import os

import pytest
from mkdocs.config import load_config
from pheasant.config import config as pheasant_config
from pheasant.plugins.mkdocs import PheasantPlugin
from pheasant.utils import read

pheasant_config = pheasant_config['jupyter']


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
    plugin_config = config['plugins']['pheasant'].config
    assert plugin_config['output_format'] == 'html'
    assert plugin_config['template_file'] == ''
    assert plugin_config['kernel_name'] == {'python': 'python3'}
    assert pheasant_config['kernel_name'] == {'python': 'python3'}
    plugin_config['output_format'] = 'markdown'
    plugin_config['template_file'] = 'template.jinja2'
    plugin_config['kernel_name'] = {'julia': 'julia'}
    template = pheasant_config['template']
    plugin.on_config(config)
    assert plugin._pheasant_output == 'markdown'
    assert pheasant_config['template'] == 'template.jinja2'
    assert pheasant_config['kernel_name'] == {'julia': 'julia',
                                              'python': 'python3'}
    pheasant_config['template'] = template


class Page:
    def __init__(self, abs_input_path):
        self.abs_input_path = abs_input_path


paths = ['docs/markdown.md', 'docs/notebook_stream_input.ipynb']


@pytest.mark.parametrize('output', ['notebook', 'markdown', 'html'])
@pytest.mark.parametrize('path', paths)
def test_on_page_read_source(plugin, config, root, stream_output,
                             output, path):
    page = Page(os.path.join(root, path))
    plugin._pheasant_output = output
    source = plugin.on_page_read_source(None, page, config)

    if not path.endswith('.ipynb'):
        assert source is None
    elif output != 'notebook':
        assert source == stream_output
    else:
        assert source.startswith('{')


@pytest.mark.parametrize('output', ['notebook', 'markdown', 'html'])
@pytest.mark.parametrize('path', paths)
def test_on_page_markdown(plugin, config, root, stream_input, stream_output,
                          output, path):
    page = Page(os.path.join(root, path))
    plugin._pheasant_output = output
    source = plugin.on_page_markdown(stream_input, page, config, None)
    if path.endswith('.ipynb'):
        assert source == stream_input
    elif output != 'notebook':
        assert source == stream_output
    else:
        assert source.startswith('{')


@pytest.mark.parametrize('output,html',
                         [('html', 'HTML'),
                          ('markdown',
                           '<h1>DEBUG MODE</h1><pre>Markdown</pre>')])
def test_on_page_content(plugin, output, html):
    plugin._pheasant_output = output
    plugin._pheasant_source = 'Markdown'
    assert plugin.on_page_content('HTML', None, None, None) == html

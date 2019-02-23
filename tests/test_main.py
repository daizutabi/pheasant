import os

import pytest
from click.testing import CliRunner

from pheasant.main import cli


def test_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    assert result.output.startswith('Pheasant version: ')


@pytest.fixture
def path():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, 'resources/pheasant/source.md')
    return os.path.abspath(path)


def test_main(path):
    assert os.path.exists(path)
    runner = CliRunner()
    result = runner.invoke(cli, [path])
    # output = ('# Pheasant Standalone\n\n## Section 1\n\n'
    #           '$\\frac{\\partial f(x)}{\\partial x}$\n\n'
    #           '<div class="pheasant-markdown pheasant-jupyter-input '
    #           'codehilite"><pre><span></span><span class="kn">import'
    #           '</span> <span class="nn">matplotlib</span>\n'
    #           '<span class="n">matplotlib</span>\n</pre></div>')
    output = ('# Pheasant Standalone\n\n## Section 1\n\n'
              '$\\frac{\\partial f(x)}{\\partial x}$\n\n'
              '```python .pheasant-markdown .pheasant-jupyter-input')
    assert result.output.startswith(output)

import os

import pytest
from click.testing import CliRunner
from mkdocs.__main__ import cli


def test_mkdocs_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0


@pytest.fixture
def path():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, '../../docs')
    return os.path.abspath(path)


def test_mkdocs_build(path):
    curdir = os.path.abspath(os.curdir)
    os.chdir(path)
    runner = CliRunner()
    result = runner.invoke(cli, 'build')
    assert result.exit_code == 0
    os.chdir(curdir)

import os

import pytest
from pelican import Pelican
from pelican.settings import read_settings
from pheasant.plugins.pelican import PheasantReader, register
from pheasant.utils import read


@pytest.fixture(scope='module')
def root():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(root, '../resources/pelican'))
    return root


@pytest.fixture(scope='module')
def reader(root):
    curdir = os.curdir
    os.chdir(root)
    settings = read_settings('pelicanconf.py')
    yield PheasantReader(settings)
    os.chdir(curdir)


def test_register():
    assert register() is None


def test_read_markdown(reader, root):
    source_path = os.path.join(root, 'content/example.md')
    content, metadata = reader.read(source_path)
    assert content.startswith('<h2>Stream</h2>')
    assert metadata['title'] == 'Pelican Example'


def test_read_notebook(reader, root):
    source_path = os.path.join(root, 'content/example.ipynb')
    content, metadata = reader.read(source_path)
    assert content.startswith('<h2>Stream</h2>')
    assert metadata['title'] == 'Pelican Example (Notebook)'

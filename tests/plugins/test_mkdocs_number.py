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
    assert number_config == {'enabled': False}


def test_pages(site_navigation, config):
    number.config.update({'enabled': True, 'configured': True})
    for k, page in enumerate(site_navigation.walk_pages()):
        source = convert(page.abs_input_path, config)
        assert number.config['pages'][k] == page.abs_input_path

import os
import platform

import pytest

try:
    from pheasant.office import common
    from pheasant.office import excel as xl
    from pheasant.office import powerpoint as pp
except ImportError:
    pass


is_not_windows = platform.system() != 'Windows'


@pytest.fixture(scope='session')
def root():
    root = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(root, '../resources/office'))
    return root


@pytest.fixture(scope='session')
def prs(root):
    path = os.path.join(root, 'presentation.pptx')
    prs = pp.open(path)
    yield prs
    prs.Close()
    common.quit('PowerPoint')


@pytest.fixture(scope='session')
def book(root):
    path = os.path.join(root, 'workbook.xlsx')
    book = xl.open(path)
    yield book
    book.Close()
    common.quit('Excel')


@pytest.fixture(scope='session')
def source_file(root):
    yield os.path.join(root, 'office.md')

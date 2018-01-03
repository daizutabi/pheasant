import os
import platform

import pytest

try:
    from pheasant.office import excel as xl
    from pheasant.office import common
except ImportError:
    pass


is_not_windows = platform.system() != 'Windows'


@pytest.fixture(scope='module')
def book(root):
    path = os.path.join(root, 'workbook.xlsx')
    book = xl.open(path)
    yield book
    book.Close()
    common.quit('Excel')


@pytest.fixture(scope='module')
def shape_first(book):
    gen = common.extract_shape_with_title(book, 'Worksheets')
    for k, shape in enumerate(gen):
        if k == 0:
            return shape


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_shape_title(shape_first):
    assert shape_first.Title == 'Rect'

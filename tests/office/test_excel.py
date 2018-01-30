import pytest

from conftest import is_not_windows

try:
    from pheasant.office import common
except ImportError:
    pass


@pytest.fixture(scope='module')
def shape_first(book):
    gen = common.extract_shape_with_title(book, 'Worksheets')
    for k, (title, i, js) in enumerate(gen):
        if k == 0:
            return book.Worksheets(i).Shapes(js[0])


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_shape_title(shape_first):
    assert shape_first.Title == 'Rect'

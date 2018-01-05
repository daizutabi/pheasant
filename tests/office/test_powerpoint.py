import os

import pytest
from conftest import is_not_windows

try:
    from pheasant.office import powerpoint as pp
    from pheasant.office import common
except ImportError:
    pass


@pytest.fixture(scope='session')
def shape_first(prs):
    for k, shape in enumerate(common.extract_shape_with_title(prs, 'Slides')):
        if k == 0:
            return shape


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_shape_title(shape_first):
    assert shape_first.Title == 'Group1'


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_get_shape_by_title(prs):
    assert common.get_shape_by_title(prs, 'Slides', 'Group1').Title == 'Group1'


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_export_shape_file(root, shape_first):
    path = os.path.join(root, 'shape.png')
    pp.export_shape(shape_first, path)
    assert os.path.exists(path)
    os.remove(path)


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_export_shape_str(root, shape_first):
    base64_str = pp.export_shape(shape_first)
    assert isinstance(base64_str, str)

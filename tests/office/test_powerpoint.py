import os
import platform

import pytest

try:
    from pheasant.office import powerpoint as pp
    from pheasant.office import common
except ImportError:
    pass


is_not_windows = platform.system() != 'Windows'


@pytest.fixture(scope='module')
def prs(root):
    path = os.path.join(root, 'presentation.pptx')
    prs = pp.open(path)
    yield prs
    prs.Close()
    common.quit('PowerPoint')


@pytest.fixture(scope='module')
def shape_first(prs):
    for k, shape in enumerate(common.extract_shape_with_title(prs, 'Slides')):
        if k == 0:
            return shape


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_shape_title(shape_first):
    assert shape_first.Title == 'Group1'


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_export_shape(root, shape_first):
    path = os.path.join(root, 'shape.png')
    common.export_shape(shape_first, path)
    assert os.path.exists(path)
    os.remove(path)
    base64_str = common.export_shape(shape_first)
    assert isinstance(base64_str, str)

import os

import pytest
from conftest import is_not_windows

try:
    from pheasant.markdown.office import powerpoint as pp
    from pheasant.markdown.office import common
except ImportError:
    pass


@pytest.fixture(scope='module')
def shape_first(prs):
    gen = common.extract_shape_with_title(prs, 'Slides')
    for k, (title, i, js) in enumerate(gen):
        if k == 0:
            return prs.Slides(i).Shapes(js[0])


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_shape_title(shape_first):
    assert shape_first.Title == 'Group1'


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_get_shape_by_title(prs, root):
    assert prs.FullName == os.path.join(root, 'presentation.pptx')
    assert prs.Slides(1).Shapes.Count == 8
    assert common.get_shape_by_title(prs, 'Slides', 'Group1').Title == 'Group1'
    assert common.get_shape_by_title(prs, 'Slides', 'Rect1').Title == 'Rect1'
    assert prs.Slides(1).Shapes(8).GroupItems.Count == 3


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

import pytest
from conftest import is_not_windows


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_powerpoint(pp):
    assert repr(pp).startswith('<PowerPoint App (')
    # assert repr(pp.presentations) == 'Presentations([])'


@pytest.mark.skipif(is_not_windows, reason='Windows only test')
def test_presentation(pp, prs):
    # assert len(pp.presentations) == 1
    assert len(prs.slides) == 1

    slide = prs.slides(1)
    assert repr(slide) == '<Slide [presentation](Slide1)>'
    assert len(slide.shapes) == 8

    shape = slide.shapes(1)
    assert repr(shape) == '<Shape [presentation](Slide1)!(Group 5)>'

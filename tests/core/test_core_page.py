import os

import pheasant
from pheasant.core.page import Pages


def test_pages():
    paths = [os.path.normpath(os.path.join(pheasant.__file__, "../../tests/docs/docs"))]
    pages = Pages(paths, "py,md")
    pages.collect()

    d = pages[0].to_dict()
    assert "path" in d

    d = pages.to_dict()
    assert "pages" in d
    assert isinstance(d['pages'], list)

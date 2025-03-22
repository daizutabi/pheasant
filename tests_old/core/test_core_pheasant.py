import os

from pheasant.core.pheasant import Pheasant


def test_pheasant(tmpdir):
    f = tmpdir.join("example.md")
    f.write("# Title\n## Section\n```python\n1\n```\n")
    path = f.strpath

    converter = Pheasant()
    output = converter.convert(path)
    assert "pheasant-header" in output
    assert "cell jupyter input" in output

    st_mtime = os.stat(path).st_mtime
    assert converter.pages[path].st_mtime == st_mtime
    converter.convert(path)
    assert converter.pages[path].st_mtime == st_mtime
    assert 'class="python">1</code>' in output

    f.write("# Title\n## Section\n```python\n2\n```\n")
    assert st_mtime < os.stat(path).st_mtime
    output = converter.convert(path)
    assert converter.pages[path].st_mtime > st_mtime
    assert converter.pages[path].st_mtime == os.stat(path).st_mtime
    assert 'class="python">2</code>' in output

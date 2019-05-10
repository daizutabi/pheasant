import os

from pheasant.renderers.embed.embed import get_language_from_path, resolve_path


def test_renderer(embed):
    output = embed.parse("~~~\nabc\n~~~\n")
    assert 'class="markdown"' in output

    output = embed.parse("{%=setup.py[1:2]%}")
    assert '<code class="python">import re</code>' in output

    output = embed.parse("{%abc.py%}")
    assert '<p style="font-color:red">File not found:' in output


def test_get_languate_from_path():
    assert get_language_from_path("a.py") == "python"
    assert get_language_from_path("a.yml") == "yaml"
    assert get_language_from_path("a.txt") == "text"


def test_resolve_path():
    assert resolve_path("abc.py?python", ".")["language"] == "python"
    path = os.path.normpath(os.path.join(__file__, "../../../../abc.py"))
    assert resolve_path("abc.py", ".")["abs_src_path"] == path
    assert resolve_path("/abc.py", ".")["abs_src_path"] == path
    assert resolve_path("/abc.py", "C:\\a\\b\\c.md")["abs_src_path"] == path

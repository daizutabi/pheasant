from pheasant.code.renderer import get_language_from_path, inspect
from pheasant.jupyter.client import get_kernel_name


def test_renderer(code):
    output = code.parse("~~~\nabc\n~~~\n")
    assert 'class="markdown"' in output

    output = code.parse("![file](setup.py<1:2>)\n")
    assert '<code class="python">import re</code>' in output

    output = code.parse("![file](abc.py)\n")
    assert output == '<p style="font-color:red">File not found: abc.py</p>\n'


def test_get_languate_from_path():
    assert get_language_from_path("a.py") == "python"
    assert get_language_from_path("a.yml") == "yaml"
    assert get_language_from_path("a.txt") == "text"


def test_inspect_error():
    kernel_name = get_kernel_name("python")
    assert inspect(kernel_name, "ABC") == "inspect error"

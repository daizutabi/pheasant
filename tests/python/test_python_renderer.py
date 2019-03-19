import re
from typing import Pattern


def test_complile_pattern():
    from pheasant.python.renderer import Python

    assert isinstance(re.compile(Python.PYTHON_CODE_PATTERN), Pattern)


def test_renderer_config(python):
    assert python.config == {}


def test_render_python(parser, python, source_simple):
    assert "python__python_code" in parser.patterns
    assert parser.patterns["python__python_code"].startswith("(?P<python__python_code>")
    assert parser.renders["python__python_code"] == python.render_python_code

    splitter = parser.split(source_simple)
    next(splitter)
    cell = next(splitter)
    assert cell.match is not None
    assert cell.context["source"] == source_simple

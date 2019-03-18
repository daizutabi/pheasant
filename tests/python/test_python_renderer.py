import re
from typing import Pattern


def test_complile_pattern():
    from pheasant.python.renderer import Python

    assert isinstance(re.compile(Python.PYTHON_CODE_PATTERN), Pattern)


def test_renderer_config(python):
    assert python.config == {}


def test_render_python(parser, python, source_simple):
    assert "Python_render_python_code" in parser.patterns
    assert parser.patterns["Python_render_python_code"].startswith(
        "(?P<Python_render_python_code>"
    )
    assert parser.renders["Python_render_python_code"] == python.render_python_code

    splitter = parser.split(source_simple)
    cell = next(splitter)
    assert cell.source == source_simple
    assert cell.context["source"] == source_simple

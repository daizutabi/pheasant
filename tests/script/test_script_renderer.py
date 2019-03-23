import re
from typing import Pattern


def test_complile_pattern():
    from pheasant.script.renderer import Script

    assert isinstance(re.compile(Script.PYTHON_CODE_PATTERN), Pattern)


def test_renderer_config(script):
    assert script.config == {}


def test_render_python(parser, script, source_simple):
    assert "script__script_code" in parser.patterns
    assert parser.patterns["script__script_code"].startswith("(?P<script__script_code>")
    assert parser.renders["script__script_code"] == script.render_script_code

    splitter = parser.split(source_simple)
    cell = next(splitter)
    assert cell.match is not None
    assert cell.context["source"] == source_simple

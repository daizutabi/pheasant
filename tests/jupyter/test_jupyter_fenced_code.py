import re
from typing import Pattern

import pytest

from pheasant.jupyter.renderer import Jupyter


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "begin\n```python\na=1\nb=1\n```\ntext",
            "begin\n```ruby inline\na=1\nb=1\n```\ntext",
        ]
    )
    return source_simple


def test_complile_pattern():
    assert isinstance(re.compile(Jupyter.FENCED_CODE_PATTERN), Pattern)
    assert isinstance(re.compile(Jupyter.INLINE_CODE_PATTERN), Pattern)


def test_renderer(jupyter):
    assert jupyter.config["fenced_code_template"] is not None
    assert jupyter.config["inline_code_template"] is not None


def test_render_fenced_code(parser, jupyter, source_simple):
    assert "jupyter__fenced_code" in parser.patterns
    assert "jupyter__inline_code" in parser.patterns

    splitter = parser.split(source_simple)
    cell = next(splitter)
    assert cell.source == "begin\n"
    cell = next(splitter)
    assert cell.render_name == "jupyter__fenced_code"
    assert cell.context.code == "a=1\nb=1"
    cell = next(splitter)
    cell = next(splitter)
    assert cell.context.language == "ruby"

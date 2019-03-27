import re
from typing import Pattern

import pytest

from pheasant.embed.renderer import Embed


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "begin\n~~~python\na=1\nb=1\n~~~\ntext",
            "begin\n~~~ruby inline\na=1\nb=1\n~~~\ntext",
        ]
    )
    return source_simple


def test_complile_pattern():
    assert isinstance(re.compile(Embed.FENCED_CODE_PATTERN), Pattern)
    assert isinstance(re.compile(Embed.INLINE_CODE_PATTERN), Pattern)


def test_renderer(embed):
    assert embed.config["fenced_code_template"] is not None


def test_render_fenced_code(parser, embed, source_simple):
    assert "embed__fenced_code" in parser.patterns
    assert "embed__inline_code" in parser.patterns

    splitter = parser.split(source_simple)
    cell = next(splitter)
    assert cell.source == "begin\n"
    cell = next(splitter)
    assert cell.render_name == "embed__fenced_code"
    assert cell.context["source"] == "a=1\nb=1"
    next(splitter)
    cell = next(splitter)
    assert cell.context["option"] == "inline"

import re
from typing import Pattern

import pytest

from pheasant.code.renderer import Code


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
    assert isinstance(re.compile(Code.FENCED_CODE_PATTERN), Pattern)
    assert isinstance(re.compile(Code.INLINE_CODE_PATTERN), Pattern)


def test_renderer(code):
    assert code.config["fenced_code_template"] is not None


def test_render_fenced_code(parser, code, source_simple):
    assert "Code_render_fenced_code" in parser.patterns
    assert "Code_render_inline_code" in parser.patterns

    splitter = parser.splitter(source_simple)
    next(splitter)
    cell = splitter.send(dict)
    assert cell["name"] is None
    assert cell["context"] == {}
    assert cell["source"] == "begin\n"
    cell = splitter.send(dict)
    assert cell["name"] == "Code_render_fenced_code"
    assert cell["context"] == {
        "mark": "~~~",
        "language": "python",
        "option": "",
        "source": "a=1\nb=1",
        "_source": cell["source"],
    }
    cell = splitter.send(dict)
    cell = splitter.send(dict)
    assert cell["context"] == {
        "mark": "~~~",
        "language": "ruby",
        "option": "inline",
        "source": "a=1\nb=1",
        "_source": cell["source"],
    }

import re
from typing import Pattern

import pytest

from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter


@pytest.fixture()
def parser():
    parser = Parser()
    return parser


@pytest.fixture()
def jupyter(parser):
    jupyter = Jupyter(parser)
    return jupyter


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "begin\n```python\na=1\nb=1\n```\ntext",
            "begin\n```ruby inline\na=1\nb=1\n```\ntext",
            "begin\n~~~bash display copy\na=1\nb=1\n~~~\ntext",
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
    assert "Jupyter_render_fenced_code" in parser.patterns
    assert "Jupyter_render_inline_code" in parser.patterns

    splitter = parser.splitter(source_simple)
    next(splitter)
    cell = splitter.send(all)
    assert cell["name"] is None
    assert cell["context"] == {}
    assert cell["source"] == "begin\n"
    cell = splitter.send(all)
    assert cell["name"] == "Jupyter_render_fenced_code"
    assert cell["context"] == {
        "mark": "```",
        "language": "python",
        "option": "",
        "code": "a=1\nb=1",
    }
    cell = splitter.send(all)
    cell = splitter.send(all)
    assert cell["context"] == {
        "mark": "```",
        "language": "ruby",
        "option": "inline",
        "code": "a=1\nb=1",
    }
    cell = splitter.send(all)
    cell = splitter.send(all)
    assert cell["context"] == {
        "mark": "~~~",
        "language": "bash",
        "option": "display copy",
        "code": "a=1\nb=1",
    }

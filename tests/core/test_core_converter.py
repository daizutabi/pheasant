import re

import pytest

from pheasant.core.converter import Converter
from pheasant.core.parser import Parser
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Linker, Number


@pytest.mark.parametrize("renderers", [[Jupyter(), Number()], ("jupyter", "number")])
def test_converter(renderers):
    converter = Converter()
    assert converter.convert("abc") == "abc"

    converter.register("markdown", renderers)
    assert len(converter.parsers) == 1

    output = converter.convert("abd\n# a\n## b\n```python\n2*3\n```\n")
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    assert output == "abd# 1. a## 1.1. b2*36"


def test_converter_getitem(converter):
    assert converter[0] == "preprocess"
    assert converter[1] == "postprocess"
    assert isinstance(converter["preprocess"], list)
    assert isinstance(converter["postprocess"], list)
    assert isinstance(converter["preprocess", 0], Jupyter)
    assert isinstance(converter["preprocess", 1], Number)
    assert isinstance(converter["postprocess", 0], Linker)
    assert isinstance(converter["preprocess", "parser"], Parser)
    assert isinstance(converter["postprocess", "parser"], Parser)
    assert isinstance(converter["preprocess", "renderer", 0], Jupyter)
    assert isinstance(converter["preprocess", "renderer", 1], Number)


def test_converter_other_special(converter):
    assert len(converter) == 2
    assert [name for name in converter] == ["preprocess", "postprocess"]
    assert repr(converter) == "<Converter['preprocess', 'postprocess'])>"
    assert repr(converter["preprocess"][0]) == "<Jupyter[2])>"

    assert callable(converter())
    assert callable(converter("preprocess"))
    assert callable(converter("preprocess", "postprocess"))


def test_multiple_parser(converter):
    source = "# title {#a#}\ntext {#a#}\n## section\n```python\n1/0\n```\n"
    number = converter['preprocess'][1]
    linker = converter['postprocess'][0]
    linker.number = number
    output = converter.convert(source, "preprocess")
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    answer = ("# 1. titletext {#a#}## 1.1. "
              "section1/0ZeroDivisionError: division by zero")
    assert output == answer
    number.reset()
    output = converter.convert(source, ["preprocess", "postprocess"])
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    answer = ("# 1. titletext [1](.#pheasant-number-a)## 1.1. "
              "section1/0ZeroDivisionError: division by zero")
    assert output == answer
    number.reset()
    output = converter.convert(source)
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    assert output == answer

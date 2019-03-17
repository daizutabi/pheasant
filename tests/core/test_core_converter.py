import re

import pytest

from pheasant.core.converter import Converter
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Number


@pytest.mark.parametrize("renderers", [[Jupyter(), Number()], ("jupyter", "number")])
def test_converter(renderers):
    converter = Converter()
    assert converter.convert("abc") == "abc"

    converter.register("markdown", renderers)
    assert len(converter.parsers) == 1

    output = converter.convert("abd\n# a\n## b\n```python\n2*3\n```\n")
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    assert output == "abd# 1. a## 1.1. b2*36"


def test_converter_other_special(converter):
    assert repr(converter) == "<Converter#converter['preprocess', 'postprocess']>"
    assert repr(converter["preprocess"]) == "<Parser#preprocess[3]>"
    assert repr(converter["preprocess", "jupyter"]) == "<Jupyter#jupyter[2]>"
    assert callable(converter())
    assert callable(converter("preprocess"))
    assert callable(converter("preprocess", "postprocess"))

    assert [repr(renderer) for renderer in converter.renderers("preprocess")] == [
        "<Jupyter#jupyter[2]>",
        "<Number#number[1]>",
    ]

    assert [repr(renderer) for renderer in converter.renderers] == [
        "<Jupyter#jupyter[2]>",
        "<Number#number[1]>",
        "<Linker#linker[1]>",
    ]


def test_multiple_parser(converter):
    source = "# title {#a#}\ntext {#a#}\n## section\n```python\n1/0\n```\n"
    number = converter["preprocess", "number"]
    linker = converter["postprocess", "linker"]
    linker.number = number
    output = converter.convert(source, "preprocess")
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    answer = (
        "# 1. titletext {#a#}## 1.1. " "section1/0ZeroDivisionError: division by zero"
    )
    assert output == answer
    number.reset()
    output = converter.convert(source, ["preprocess", "postprocess"])
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    answer = "# 1. titletext 1## 1.1. " "section1/0ZeroDivisionError: division by zero"
    assert output == answer
    number.reset()
    output = converter.convert(source)
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    assert output == answer

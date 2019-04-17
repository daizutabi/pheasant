import re

import pytest

from pheasant.core.converter import Converter
from pheasant.renderers.number.number import Header


def test_converter_init(jupyter):
    converter = Converter()
    converter.register([jupyter, Header()])
    assert len(converter.parsers) == 1


def test_converter(jupyter):
    converter = Converter()
    converter.register([jupyter, Header()], "markdown")
    output = converter.parse("abd\n# a\n## b\n```python\n2*3\n```\n", "markdown")
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    assert output == "abd# 1 a## 1.1 b2*36"

    with pytest.raises(ValueError):
        converter.register([jupyter], "markdown")

    converter.update_config({"jupyter": {"a": "b"}})
    assert jupyter.config["a"] == "b"


def test_converter_special_function(converter):
    assert repr(converter) == "<Converter#converter['preprocess', 'postprocess']>"
    assert repr(converter["preprocess"]) == "<Parser#preprocess[3]>"
    assert repr(converter["preprocess", "jupyter"]) == "<Jupyter#jupyter[2]>"
    with pytest.raises(KeyError):
        converter["preprocess", "abc"]

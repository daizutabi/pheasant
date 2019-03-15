import re

from pheasant.core.converter import Converter
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Number


def test_converter():
    converter = Converter()
    assert converter.convert("abc") == "abc"

    jupyter = Jupyter()
    number = Number()
    converter.register('markdown', [jupyter, number])
    converter.parsers
    converter.renderers
    assert len(converter.parsers) == 1

    output = converter.convert("abd\n# a\n## b\n```python\n2*3\n```\n")
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    assert output == "abd# 1. a## 1.1. b2*36"

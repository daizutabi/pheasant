import re

import pytest

from pheasant.core.converter import Converter
from pheasant.jupyter.renderer import Jupyter
from pheasant.number.renderer import Number


@pytest.mark.parametrize("renderers", [(Jupyter(), Number()), ("jupyter", "number")])
def test_converter(renderers):
    converter = Converter()
    assert converter.convert("abc") == "abc"

    converter.register("markdown", renderers)
    assert len(converter.parsers) == 1

    output = converter.convert("abd\n# a\n## b\n```python\n2*3\n```\n")
    output = re.sub(r"(\<.*?\>)|\n", "", output)
    assert output == "abd# 1. a## 1.1. b2*36"



j = Jupyter()
# def test_converter_multi_parser():
#     converter = Converter()
#     converter.register("preprocess", ['jupyter', 'number'])
#     converter.register("postprocess", ['linker'])
#     assert len(converter.parsers) == 2
#
#     output = converter.convert("# t{#a#}\nabd {#a}\n# a\n## b\n```python\n2*3\n```\n")
#     output = re.sub(r"(\<.*?\>)|\n", "", output)
#     assert output == "abd# 1. a## 1.1. b2*36"
#     print(output)
#
#     converter.renderers

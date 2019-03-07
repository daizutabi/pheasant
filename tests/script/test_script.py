from pheasant.script.config import config
from pheasant.script.converter import convert, initialize


def test_initialize():
    assert initialize() is None
    assert config['OPTION_PATTERN'] is not None
    assert config['COMMENT_PATTERN'] is not None
    assert config['SEPARATOR_PATTERN'] is not None


def test_converter_markdown_only():
    source = '\n\n# # Test\n\n# ## Section\n'
    convert(source)

import ast

node = ast.parse('#dfd\n#e')

node.body

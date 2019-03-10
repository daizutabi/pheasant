from pheasant.script.config import config
from pheasant.script.converter import convert, initialize
from pheasant.script.formatter import Formatter


def test_initialize():
    assert initialize() is None
    assert Formatter.OPTION_PATTERN is not None
    assert Formatter.COMMENT_PATTERN is not None
    assert "ESCAPE_PATTERN" in config


def test_converter_markdown_only():
    source = "\n\n# # Test\n\n# ## Section\n\n\n"
    assert convert(source) == "# Test\n\n## Section\n"


def test_converter_code_only():
    source = "def func():\n    return 1\n\n"
    assert convert(source) == "```python\ndef func():\n    return 1\n```\n"


def test_converter_mixed():
    source = "# # Test\ndef func():\n    return 1\n# abc\na=1\n#xyz\n"
    answer = (
        "# Test\n\n```python\ndef func():\n    return 1"
        "\n```\n\nabc\n\n```python\na=1\n```\n\n#xyz\n"
    )
    assert convert(source) == answer


def test_converter_mixed_blank_lines():
    source = "z=1\n\n\n# # Test\ndef func():\n    return 1\n# abc\n\n# a\n"
    answer = (
        "```python\nz=1\n```\n\n# Test\n\n```python\ndef func():\n"
        "    return 1\n```\n\nabc\n\na\n"
    )
    assert convert(source) == answer


def test_converter_separator():
    source = "# abc\na=1\n# -\nb=1\n# ade\n"
    answer = "abc\n\n```python\na=1\n```\n\n```python\nb=1\n```\n\nade\n"
    assert convert(source) == answer


def test_converter_option():
    source = "\n# abc\n\na=1  # -inline\nb=1\n# ----\nc=1  # -hide\n\n# end."
    answer = (
        "abc\n\n```python inline\na=1\nb=1\n```\n\n"
        "```python hide\nc=1\n```\n\nend.\n"
    )
    assert convert(source) == answer


def test_converter_escape():
    source = (
        "# # Test\n"
        "print(1)\n"
        "print(2)\n"
        "# xあ\n"
        "# いy\n"
        "# ```\n"
        "# ~~~python\n"
        "# a = 1\n"
        "# b = 1\n"
        "# ~~~\n"
        "# a\n"
        "# b\n"
        "# ```\n"
        "# abc\n"
        "# def\n"
    )
    answer = (
        "# Test\n\n```python\nprint(1)\nprint(2)\n```\n\nxあい"
        "y\n\n```\n~~~python\na = 1\nb = 1\n~~~\na\nb\n```\n\nabc def\n"
    )
    assert convert(source) == answer


def test_converter_escape_nest():
    source = (
        "# # Test\n"
        "# ~~~~\n"
        "# ~~~\n"
        "# ```python\n"
        "# a = 1\n"
        "# b = 1\n"
        "# ```\n"
        "# a\n"
        "# b\n"
        "# ~~~\n"
        "# ~~~~\n"
        "# abc\n"
    )
    answer = (
        "# Test\n\n~~~~\n~~~\n```python\na = 1\nb = 1\n```\na\nb\n~~~\n~~~~\n\nabc\n"
    )
    assert convert(source) == answer

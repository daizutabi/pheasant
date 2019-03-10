import pytest

from pheasant.script.formatter import Formatter


@pytest.mark.parametrize(
    "source, output",
    [
        ("# abc\n# def\n# ghi.", "abc def ghi.\n"),
        ("# abc\n# あいう\n# ghi.", "abc あいう ghi.\n"),
        ("# abc\n# あいう\n# えお.", "abc あいうえお.\n"),
        ("# abか\n# あいう\n# えお.", "abかあいうえお.\n"),
        ("# abc\n\n# def\n# gh.", "abc\n\ndef gh.\n"),
        ("# abc\n\n\n\n# deあ\n# いgh.", "abc\n\n\n\ndeあいgh.\n"),
    ],
)
def test_formatter_markdown(source, output):
    formatter = Formatter(source)
    assert formatter("Markdown", 0, len(formatter) - 1) == output


@pytest.mark.parametrize(
    "source, output",
    [
        ("# ~~~ python\n# def\n# ghi.\n# ~~~", "~~~ python\ndef\nghi.\n~~~\n"),
    ],
)
def test_formatter_escape(source, output):
    formatter = Formatter(source)
    assert formatter("Escape", 0, len(formatter) - 1) == output


@pytest.mark.parametrize(
    "source, output",
    [
        ("a = 1\nb = 1", "```python\na = 1\nb = 1\n```\n"),
        ("a = 1\n\n\nb = 1", "```python\na = 1\n\nb = 1\n```\n"),
        ("a = 1  # -option\n\n\nb = 1", "```python option\na = 1\n\nb = 1\n```\n"),
    ],
)
def test_formatter_code(source, output):
    formatter = Formatter(source)
    assert formatter("Code", 0, len(formatter) - 1) == output

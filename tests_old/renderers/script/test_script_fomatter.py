import pytest

from pheasant.renderers.script.formatter import format_source


@pytest.mark.parametrize(
    "source, output",
    [
        ("abc\ndef\nghi.\n", "abc def ghi.\n"),
        ("abc\nあいう\nghi.\n", "abcあいうghi.\n"),
        ("abc\nあいう\nえお.\n", "abcあいうえお.\n"),
        ("abか\nあいう\nえお.\n", "abかあいうえお.\n"),
    ],
)
def test_formatter_markdown(source, output):
    print(source, format_source(source))
    assert format_source(source) == output

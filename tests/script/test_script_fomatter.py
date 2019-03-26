import pytest

from pheasant.script.formatter import format_source


@pytest.mark.parametrize(
    "source, output",
    [
        ("abc\ndef\nghi.\n", "abc def ghi.\n"),
        ("abc\nあいう\nghi.\n", "abc あいう ghi.\n"),
        ("abc\nあいう\nえお.\n", "abc あいうえお.\n"),
        ("abか\nあいう\nえお.\n", "abかあいうえお.\n"),
    ],
)
def test_formatter_markdown(source, output):
    print(source, format_source(source))
    assert format_source(source) == output

import pytest

from pheasant.script.formatter import format_comment


@pytest.mark.parametrize(
    "source, output",
    [
        ("abc\ndef\nghi.", "abc def ghi.\n"),
        ("abc\nあいう\nghi.", "abc あいう ghi.\n"),
        ("abc\nあいう\nえお.", "abc あいうえお.\n"),
        ("abか\nあいう\nえお.", "abかあいうえお.\n"),
        ("abc\n\ndef\ngh.", "abc\n\ndef gh.\n"),
        ("abc\n\n\n\ndeあ\nいgh.", "abc\n\n\n\ndeあいgh.\n"),
    ],
)
def test_formatter_markdown(source, output):
    assert format_comment(source) == output

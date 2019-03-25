import pytest

from pheasant.script.formatter import format_comment


@pytest.mark.parametrize(
    "source, output",
    [
        ("#abc\n# def\n# ghi.\n", "# abc def ghi.\n"),
        ("#  abc\n# あいう\n#ghi.\n", "# abc あいう ghi.\n"),
        ("# abc\n# あいう\n#えお.\n", "# abc あいうえお.\n"),
        ("# abか\n# あいう\n#えお.\n", "# abかあいうえお.\n"),
    ],
)
def test_formatter_markdown(source, output):
    print(source, format_comment(source))
    assert format_comment(source) == output

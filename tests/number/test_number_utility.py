import pytest

from pheasant.number.renderer import normalize_number_list, split_tag


@pytest.mark.parametrize(
    "input,text,tag",
    [
        ("text", "text", ""),
        ("text {#tag#}", "text", "tag"),
        ("{#tag#} text", "text", "tag"),
    ],
)
def test_split_label(input, text, tag):
    assert split_tag(input) == (text, tag)


@pytest.mark.parametrize(
    "kind,number_list,page_index,output",
    [
        ("header", [1], 1, [1]),
        ("header", [1, 2], [3], [3, 2]),
        ("header", [0, 2], 2, [2]),
        ("header", [0, 2], 1, [0, 2]),
        ("header", [0, 2, 1], 2, [2, 1]),
        ("figure", [3], 1, [3]),
        ("figure", [3], [4, 2], [4, 2, 3]),
        ("figure", [3, 1], 2, [3, 1]),
    ],
)
def test_normalized_number_list(kind, number_list, page_index, output):
    assert normalize_number_list(kind, number_list, page_index) == output

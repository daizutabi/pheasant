import pytest

from pheasant.number import initialize
from pheasant.number.header import (
    convert,
    header_splitter,
    normalize_number_list,
    render,
    split_label,
)


@pytest.mark.parametrize(
    "input,text,label",
    [
        ("text", "text", ""),
        ("text {#label#}", "text", "label"),
        ("{#label#} text", "text", "label"),
    ],
)
def test_split_label(input, text, label):
    assert split_label(input) == (text, label)


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


@pytest.fixture
def source():
    yield """
# header {#H1#}

A text

## header {#H1.1#}

#Fig. figure {#F1#}

## header {#H1.2#}

#figure figure {#F2#}

# header {#H2#}

## header {#H2.1#}

#Table table {#T1#}

A text

#Tab. table {#T2#}

### header {#H2.1.1#}

A text
""".strip()


def test_header_splitter(source):
    for k, splitted in enumerate(header_splitter(source)):
        if isinstance(splitted, str):
            assert splitted == "A text"
        else:
            assert splitted["title"] == splitted["kind"]
            number_list = "[" + splitted["label"][1:].replace(".", ",") + "]"
            assert splitted["number_list"] == eval(number_list)
        if k == 0:
            assert splitted["cursor"] == 0
        elif k == 2:
            assert splitted["cursor"] == 25
        elif k == 3:
            assert splitted["cursor"] == 55


def test_header_splitter_invalid_div_escape():
    source = (
        '# a\n\n<div>\n\n# b\n</div>\n\n<div class="pheasant-code">\n'
        "<pre>abc\n\n# c\ndef\n</pre></div>\n\n## d\n\ntext.\n"
    )
    for k, splitted in enumerate(header_splitter(source)):
        if k == 0:
            assert isinstance(splitted, dict) and splitted["title"] == "a"
        elif k == 1:
            assert splitted == "<div>"
        elif k == 2:
            assert isinstance(splitted, dict) and splitted["title"] == "b"
        elif k == 3:
            answer = (
                '</div>\n\n<div class="pheasant-code">\n'
                "<pre>abc\n\n# c\ndef\n</pre></div>"
            )
            assert splitted == answer
        elif k == 4:
            assert isinstance(splitted, dict) and splitted["title"] == "d"
        elif k == 5:
            assert splitted == "text."


def test_header_splitter_valid_div_escape():
    source = (
        '# a\n\n<div class="pheasant-code">\n'
        "<pre>abc\n\n# b\n\ndef\n</pre></div>\n\n## c\n\ntext.\n"
    )
    for k, splitted in enumerate(header_splitter(source)):
        if k == 0:
            assert isinstance(splitted, dict) and splitted["title"] == "a"
        elif k == 1:
            answer = (
                '<div class="pheasant-code">\n<pre>abc\n\n' "# b\n\ndef\n</pre></div>"
            )
            assert splitted == answer
        elif k == 2:
            assert isinstance(splitted, dict) and splitted["title"] == "c"
        elif k == 3:
            assert splitted == "text."


def test_initialize():
    initialize()


@pytest.fixture
def source_input():
    yield """
# header1 {#H1#}

A text

## header2 {#H1.1#}

#Fig. figure {#F1#}

![png](figure1.png)

#Fig. figure {#F2#}

<!-- begin -->
![png](figure2.png)

![png](figure3.png)
<!-- end -->

#Tab. table {#T1#}

First Header | Second Header
------------ | -------------
Content Cell | Content Cell
Content Cell | Content Cell
""".strip()


@pytest.fixture
def source_output():
    yield """
# <span id="PN-H1"><span class="pheasant-header-number">1.</span>++
<span class="pheasant-header-title">header1</span></span>
A text
## <span id="PN-H1.1"><span class="pheasant-header-number">1.1.</span>++
<span class="pheasant-header-title">header2</span></span>
<div class="PN-figure" id="PN-F1">
<p><img alt="png" src="figure1.png" /></p>
<p class="pheasant-figure">
<span class="name">Figure</span>
<span class="number">1</span>
<span class="title">figure</span></p>
</div>
<div class="PN-figure" id="PN-F2">
<p><img alt="png" src="figure2.png" /></p>
<p><img alt="png" src="figure3.png" /></p>
<p class="pheasant-figure">
<span class="name">Figure</span>
<span class="number">2</span>
<span class="title">figure</span></p>
</div>
<div class="PN-table" id="PN-T1">
<p class="pheasant-table">
<span class="name">Table</span>
<span class="number">1</span>
<span class="title">table</span></p>
<table>
<thead>
<tr>
<th>First Header</th>
<th>Second Header</th>
</tr>
</thead>
<tbody>
<tr>
<td>Content Cell</td>
<td>Content Cell</td>
</tr>
<tr>
<td>Content Cell</td>
<td>Content Cell</td>
</tr>
</tbody>
</table>
</div>
""".strip()


def test_renderer(source_input, source_output):
    label = {}
    o = "\n".join(list(render(source_input, label)))
    o2 = source_output.replace("++\n", " ")

    for x, y in zip(o.split("\n"), o2.split("\n")):
        assert x.replace("pheasant-number", "PN") == y


@pytest.fixture
def source_label():
    yield """
# header {#a#}

A text

## header {#b#}

#Fig. figure {#c#}

![png](figure1.png)

#Fig. figure {#d#}

![png](figure2.png)

""".strip()


def test_label(source_label):
    source, label = convert(source_label)
    assert label["a"] == {
        "kind": "header",
        "number_list": [1],
        "id": "pheasant-number-a",
    }
    assert label["b"] == {
        "kind": "header",
        "number_list": [1, 1],
        "id": "pheasant-number-b",
    }
    assert label["c"] == {
        "kind": "figure",
        "number_list": [1],
        "id": "pheasant-number-c",
    }
    assert label["d"] == {
        "kind": "figure",
        "number_list": [2],
        "id": "pheasant-number-d",
    }
    source, label = convert(source_label, page_index=[5])
    assert label["a"] == {
        "kind": "header",
        "number_list": [5],
        "id": "pheasant-number-a",
    }
    assert label["b"] == {
        "kind": "header",
        "number_list": [5, 1],
        "id": "pheasant-number-b",
    }
    assert label["c"] == {
        "kind": "figure",
        "number_list": [5, 1],
        "id": "pheasant-number-c",
    }
    assert label["d"] == {
        "kind": "figure",
        "number_list": [5, 2],
        "id": "pheasant-number-d",
    }

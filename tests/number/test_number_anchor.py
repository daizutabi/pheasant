import pytest


def test_without_number(anchor, parser_header, parser_anchor, source_simple):
    assert anchor.header is None

    with pytest.raises(ValueError):
        "".join(parser_anchor.parse(source_simple))


def test_with_number(anchor, header, parser_header, parser_anchor, source_simple):
    list(parser_header.parse(source_simple))
    assert len(header.label_context) == 2
    anchor.header = header
    assert anchor.header is header


def test_label_context(anchor, parser_header, source_simple):
    assert anchor.header is not None
    label_context = {
        "label-a": {
            "kind": "header",
            "number_list": [1],
            "id": "pheasant-header-label-a",
            "abs_src_path": ".",
        },
        "label-b": {
            "kind": "figure",
            "number_list": [2],
            "id": "pheasant-header-label-b",
            "abs_src_path": ".",
        },
    }
    assert anchor.header.label_context == label_context


@pytest.fixture()
def source_parsed(anchor, parser_header, source_simple):
    anchor.header.reset()
    source = "".join(parser_header.parse(source_simple))
    return source


def test_render_anchor(anchor, parser_anchor, source_parsed):
    assert "Anchor_render_label" in parser_anchor.patterns
    assert parser_anchor.patterns["Anchor_render_label"].startswith(
        "(?P<Anchor_render_label>"
    )
    assert parser_anchor.renders["Anchor_render_label"] == anchor.render_label

    splitter = parser_anchor.split(source_parsed)
    cell = next(splitter)
    assert cell.name is None
    assert cell.context == {}
    answer = (
        'begin\n# <span id="pheasant-header-label-a">1. title</span>\n' "text a Figure "
    )
    assert cell.source == answer
    cell = next(splitter)
    assert cell.name == "Anchor_render_label"
    assert cell.context == {"label": "label-b", "_source": cell.source}
    assert cell.context["label"] in anchor.header.label_context


def test_parse_anchor(anchor, parser_anchor, source_parsed):
    source = "".join(parser_anchor.parse(source_parsed))
    answer = (
        'begin\n# <span id="pheasant-header-label-a">1. title</span>\n'
        'text a Figure <a href=".#pheasant-header-label-b">2</a>\n'
        "## 1.1. section a\ntext b\n### 1.1.1. subsection\n"
        '## 1.2. section b\ntext c\n<div class="pheasant-header-figure">'
        "<p>figure content a1\nfigure content a2\ntext d</p>\n"
        "<p>Figure 1 figure title a</p></div>\n"
        '<div class="pheasant-header-figure" id="pheasant-header-label-b">'
        "<p>figure content b1\nfigure content b2</p>\n"
        '<p>Figure 2 figure title b Section <a href=".#pheasant-header-label-a">1</a>'
        '</p></div>\nend <span style="color: red;">'
        "Unknown label: 'label-c'</span>"
    )
    assert source == answer

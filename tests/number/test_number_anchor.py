import pytest


def test_without_number(anchor, parser_header, parser_anchor, source_simple):
    assert anchor.header is None

    with pytest.raises(ValueError):
        "".join(parser_anchor.parse(source_simple))


def test_with_number(anchor, header, parser_header, parser_anchor, source_simple):
    list(parser_header.parse(source_simple))
    assert len(header.tag_context) == 2
    anchor.header = header
    assert anchor.header is header


def test_tag_context(anchor, parser_header, source_simple):
    assert anchor.header is not None
    tag_context = {
        "tag-a": {
            "kind": "header",
            "number_list": [1],
            "number_string": "1",
            "id": "pheasant-header-tag-a",
            "abs_src_path": ".",
        },
        "tag-b": {
            "kind": "figure",
            "number_list": [2],
            "number_string": "2",
            "id": "pheasant-header-tag-b",
            "abs_src_path": ".",
        },
    }
    assert anchor.header.tag_context == tag_context


@pytest.fixture()
def source_parsed(anchor, parser_header, source_simple):
    anchor.header.reset()
    source = "".join(parser_header.parse(source_simple))
    return source


def test_render_anchor(anchor, parser_anchor, source_parsed):
    assert "anchor__tag" in parser_anchor.patterns
    assert parser_anchor.patterns["anchor__tag"].startswith(
        "(?P<anchor__tag>"
    )
    assert parser_anchor.renders["anchor__tag"] == anchor.render_tag

    splitter = parser_anchor.split(source_parsed)
    context = next(splitter)
    answer = (
        'begin\n# <span id="pheasant-header-tag-a">1 title</span>\n' "text a Figure "
    )
    assert context.source == answer
    context = next(splitter)
    assert context.render_name == "anchor__tag"
    assert context.group.tag == "tag-b"


def test_parse_anchor(anchor, parser_anchor, source_parsed):
    source = "".join(parser_anchor.parse(source_parsed))
    answer = (
        'begin\n# <span id="pheasant-header-tag-a">1 title</span>\n'
        'text a Figure [2](.#pheasant-header-tag-b)\n'
        "## 1.1 section a\ntext b\n### 1.1.1 subsection\n"
        '## 1.2 section b\ntext c\n<div class="pheasant-header-figure">'
        "<p>figure content a1\nfigure content a2\ntext d</p>\n"
        "<p>Figure 1 figure title a</p></div>\n"
        '<div class="pheasant-header-figure" id="pheasant-header-tag-b">'
        "<p>figure content b1\nfigure content b2</p>\n"
        '<p>Figure 2 figure title b Section [1](.#pheasant-header-tag-a)'
        '</p></div>\nend <span style="color: red;">'
        "Unknown tag: 'tag-c'</span>"
    )
    assert source == answer

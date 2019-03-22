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
            "abs_src_path": ".",
        },
        "tag-b": {
            "kind": "figure",
            "number_list": [1, 1],
            "number_string": "1.1",
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
    assert parser_anchor.patterns["anchor__tag"].startswith("(?P<anchor__tag>")
    assert parser_anchor.renders["anchor__tag"] == anchor.render_tag

    splitter = parser_anchor.split(source_parsed)
    next(splitter)
    cell = next(splitter)
    assert cell.render_name == "anchor__tag"
    assert cell.context["tag"] == "tag-b"


def test_parse_anchor(anchor, parser_anchor, source_parsed):
    output = "".join(parser_anchor.parse(source_parsed))
    output = output.replace("span", "S").replace("class=", "C").replace("div", "D")
    answer = "\n".join([
        '# <S C"header"><S C"number">1</S> <S C"title" id="tag-a">Title</S></S>',
        '## <S C"header"><S C"number">1.1</S> <S C"title">Section A</S></S>',
        'Text [1.1](.#tag-b)',
        '## <S C"header"><S C"number">1.2</S> <S C"title">Section B</S></S>',
        '## <S C"header"><S C"number">1.3</S> <S C"title">Subsection C</S></S>',
        'Text [1](.#tag-a)',
        '<D C"figure"><D C"content" id="tag-b"><D>Content A</D></D>',
        '<p><S C"prefix">Figure</S> <S C"number">1.1</S>',
        '<S C"title">Figure A</S></D>\n'
    ])
    assert output == answer

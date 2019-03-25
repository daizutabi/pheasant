import pytest


def test_without_number(anchor, source_simple):
    assert anchor.header is None

    with pytest.raises(ValueError):
        anchor.parse(source_simple)


def test_with_number(anchor, header, source_simple):
    list(header.parse(source_simple))  # DO PARSE
    assert len(header.tag_context) == 2
    anchor.header = header
    assert anchor.header is header


def test_tag_context(anchor, source_simple):
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
def source_parsed(anchor, header, source_simple):
    anchor.header.reset()
    return header.parse(source_simple)


def test_render_anchor(anchor, source_parsed):
    assert "anchor__tag" in anchor.parser.patterns
    assert anchor.parser.patterns["anchor__tag"].startswith("(?P<anchor__tag>")
    assert anchor.parser.renders["anchor__tag"] == anchor.render_tag

    splitter = anchor.parser.split(source_parsed)
    next(splitter)
    cell = next(splitter)
    assert cell.render_name == "anchor__tag"
    assert cell.context["tag"] == "tag-b"


def test_parse_anchor(anchor, source_parsed):
    output = anchor.parse(source_parsed)
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
        '<S C"title">Figure A</S></p></D>\n'
    ])
    assert output == answer

import re
from typing import Pattern


def test_complile_pattern():
    from pheasant.number.renderer import Header

    assert isinstance(re.compile(Header.HEADER_PATTERN), Pattern)
    assert isinstance(re.compile(Header.TAG_PATTERN), Pattern)


def test_renderer(header):
    assert header.config["__dummy__"] == "test"
    assert "kind" in header.config
    assert header.config["header_template"] is not None
    assert header.header_kind == {
        "": "header",
        "fig": "figure",
        "tab": "table",
        "cod": "code",
        "fil": "file",
    }


def test_render_header(parser_header, header, source_simple):
    assert "header__header" in parser_header.patterns
    assert parser_header.patterns["header__header"].startswith("(?P<header__header>")
    assert parser_header.renders["header__header"] == header.render_header

    splitter = parser_header.split(source_simple)
    cell = next(splitter)
    assert cell.render_name == "header__header"
    assert cell.context["prefix"] == "#"
    assert cell.match.group() == "# Title {#tag-a#}\n"


def test_join(parser_header, header, source_simple):
    output = "".join(parser_header.parse(source_simple))
    output = output.replace("span", "S").replace("class=", "C").replace("div", "D")
    answer = "\n".join(
        [
            '# <S C"header"><S C"number">1</S> <S C"title" id="tag-a">Title</S></S>',
            '## <S C"header"><S C"number">1.1</S> <S C"title">Section A</S></S>',
            "Text {#tag-b#}",
            '## <S C"header"><S C"number">1.2</S> <S C"title">Section B</S></S>',
            '## <S C"header"><S C"number">1.3</S> <S C"title">Subsection C</S></S>',
            "Text {#tag-a#}",
            '<D C"figure"><D C"content" id="tag-b"><D>Content A</D></D>',
            '<p><S C"prefix">Figure</S> <S C"number">1.1</S>',
            '<S C"title">Figure A</S></p></D>\n',
        ]
    )
    assert output == answer

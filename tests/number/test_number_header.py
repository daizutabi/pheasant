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
    assert header.page_index == 1
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
    assert cell.source == "begin\n"
    cell = next(splitter)
    assert cell.render_name == "header__header"
    assert cell.context.prefix == "#"
    assert cell.context._source == "# title {#tag-a#}\n"


def test_join(parser_header, header, source_simple):
    output = "".join(parser_header.parse(source_simple))
    answer = "".join(
        [
            'begin\n# <span id="pheasant-header-tag-a">1 title</span>\n',
            "text a Figure {#tag-b#}\n## 1.1 section a\ntext b\n",
            "### 1.1.1 subsection\n## 1.2 section b\ntext c\n",
            '<div class="pheasant-header-figure">',
            "<p>figure content a1\nfigure content a2\ntext d</p>\n",
            "<p>Figure 1 figure title a</p></div>\n",
            '<div class="pheasant-header-figure" id="pheasant-header-tag-b">',
            "<p>figure content b1\nfigure content b2</p>\n",
            "<p>Figure 2 figure title b Section {#tag-a#}</p></div>\n",
            "end {#tag-c#}",
        ]
    )
    assert output == answer

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


def test_render_header(header, source_simple):
    assert "header__header" in header.parser.patterns
    assert header.parser.patterns["header__header"].startswith("(?P<header__header>")
    assert header.parser.renders["header__header"] == header.render_header

    splitter = header.parser.split(source_simple)
    cell = next(splitter)
    assert cell.render_name == "header__header"
    assert cell.context["prefix"] == "#"
    assert cell.match.group() == "# Title {#tag-a#}\n"


def test_join(header, source_simple):
    output = header.parse(source_simple)
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


def test_ignore(header):
    from pheasant.number.renderer import Header

    header = Header()
    assert header.meta["ignored_depth"] == 100

    output = header.parse("# title\n## section\n### subsection\n")
    assert "number" in output
    assert header.number_list["header"] == [1, 1, 1, 0, 0, 0]

    output = header.parse("## #section\n")
    assert "number" not in output
    assert header.number_list["header"] == [1, 1, 1, 0, 0, 0]
    assert header.meta["ignored_depth"] == 1

    output = header.parse("### subsection\n")
    assert "number" not in output

    output = header.parse("## section\n")
    assert "number" in output
    assert header.number_list["header"] == [1, 2, 0, 0, 0, 0]
    assert header.meta["ignored_depth"] == 100

    output = header.parse("## ##section\n")
    assert "number" not in output
    assert header.number_list["header"] == [1, 2, 0, 0, 0, 0]
    assert header.meta["ignored_path"] == set(["."])

    output = header.parse("# title\n")
    assert "number" not in output


def test_inline_code(header):
    output = header.parse("#FIG title {{2*3}}\n")
    assert '<div class="content">{{2*3}}</div>' in output


def test_get_content(header):
    output = header.parse("#FIG title\n \n \n\nabc\n\ndef\n")
    assert '<div class="content"><p>abc</p></div>' in output
    assert "</div>\n\ndef" in output

    output = header.parse("#FIG title\n \n \n\n# test\n")
    assert '<div class="content"># <span class="header"' in output

    from pheasant.code.renderer import Embed
    embed = Embed()
    embed.parser = header.parser

    source = "#fig title\n~~~\na\n\nb\n~~~\n \n\ntest\n"
    output = header.parse(source)
    assert '<div class="content"><p>a</p>\n<p>b</p></div>' in output

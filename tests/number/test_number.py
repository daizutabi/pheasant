import re
from typing import Pattern


def test_complile_pattern():
    from pheasant.number.renderer import Number

    assert isinstance(re.compile(Number.HEADER_PATTERN), Pattern)
    assert isinstance(re.compile(Number.LABEL_PATTERN), Pattern)


def test_renderer(number):
    assert number.config["__dummy__"] == "test"
    assert "kind" in number.config
    assert number.config["header_template"] is not None
    assert number.page_index == 1
    assert number.header_kind == {
        "": "header",
        "fig": "figure",
        "tab": "table",
        "cod": "code",
        "fil": "file",
    }


def test_render_header(parser_number, number, source_simple):
    assert "Number_render_header" in parser_number.patterns
    assert parser_number.patterns["Number_render_header"].startswith(
        "(?P<Number_render_header>"
    )
    assert parser_number.renders["Number_render_header"] == number.render_header

    splitter = parser_number.splitter(source_simple)
    next(splitter)
    cell = splitter.send(dict)
    assert cell["name"] is None
    assert cell["context"] == {}
    assert cell["source"] == "begin\n"
    cell = splitter.send(dict)
    assert cell["name"] == "Number_render_header"
    assert cell["context"] == {"prefix": "#", "kind": "", "title": "title {#label-a#}"}
    assert cell["source"] == "# title {#label-a#}\n"


def test_join(parser_number, number, source_simple):
    output = "".join(parser_number.parse(source_simple))
    answer = """begin
        # <span id="pheasant-number-label-a">1. title</span>
        text a Figure {#label-b#}
        ## 1.1. section a
        text b
        ### 1.1.1. subsection
        ## 1.2. section b
        text c
        <div class="pheasant-number-figure">
        <p>figure content a1
        figure content a2
        text d</p>
        <p>Figure 1 figure title a</p>
        </div>
        <div class="pheasant-number-figure" id="pheasant-number-label-b">
        <p>figure content b1
        figure content b2</p>
        <p>Figure 2 figure title b Section {#label-a#}</p>
        </div>
        end {#label-c#}""".replace(
        "        ", ""
    )
    assert output == answer
    label_context = {
        "label-a": {
            "kind": "header",
            "number_list": [1],
            "id": "pheasant-number-label-a",
            "abs_src_path": ".",
        },
        "label-b": {
            "kind": "figure",
            "number_list": [2],
            "id": "pheasant-number-label-b",
            "abs_src_path": ".",
        },
    }
    assert number.label_context == label_context

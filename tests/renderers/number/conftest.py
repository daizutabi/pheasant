import pytest

from pheasant.renderers.number.number import Anchor, Header


@pytest.fixture(scope="module")
def header():
    header = Header(config={"__dummy__": "test"})
    return header


@pytest.fixture(scope="module")
def anchor():
    anchor = Anchor()
    return anchor


@pytest.fixture()
def source_simple():
    source_simple = "\n".join(
        [
            "# Title {#tag-a#}",
            "## Section A",
            "Text {#tag-b#}",
            "## Section B",
            "## Subsection C",
            "Text {#tag-a#}",
            "#Fig Figure A {#tag-b#}",
            "<div>Content A</div>",
        ]
    )
    return source_simple

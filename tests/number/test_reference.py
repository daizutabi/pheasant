import pytest
from pheasant.number import initialize
from pheasant.number.header import convert as convert_header
from pheasant.number.reference import convert


@pytest.fixture
def source_input():
    yield """
{#b#}

# header {#a#}

A Text {#b#}

## header {#b#}

{#a#}, {#b#}
""".strip()


@pytest.fixture
def source_output():
    yield """
[1.1](#pheasant-b)

# <span id="pheasant-a">1 header</span>

A Text [1.1](#pheasant-b)

## <span id="pheasant-b">1.1 header</span>

[1](#pheasant-a), [1.1](#pheasant-b)
""".strip()


def test_renderer(source_input, source_output):
    initialize()
    source, tag = convert_header(source_input)
    for key in tag:
        tag[key]['ref'] = '#' + tag[key]['id']
    output = convert(source, tag)
    for lines in zip(output.split('\n'), source_output.split('\n')):
        assert lines[0] == lines[1]

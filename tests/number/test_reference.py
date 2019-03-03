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
[1.1](#pheasant-number-b)

# <span id="pheasant-number-a"><span class="pheasant-header-number">1</span>
<span class="pheasant-header-title">header</span></span>

A Text [1.1](#pheasant-number-b)

## <span id="pheasant-number-b"><span class="pheasant-header-number">1.1</span>
<span class="pheasant-header-title">header</span></span>

[1](#pheasant-number-a), [1.1](#pheasant-number-b)
""".strip()


def test_renderer(source_input, source_output):
    initialize()
    source, tag = convert_header(source_input)
    for key in tag:
        tag[key]['ref'] = '#' + tag[key]['id']
    output = convert(source, tag)
    source_output = source_output.replace('</span>\n<span ', '</span> <span ')
    for lines in zip(output.split('\n'), source_output.split('\n')):
        assert lines[0] == lines[1]

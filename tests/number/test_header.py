import pytest
from pheasant.number import initialize
from pheasant.number.header import (convert, header_splitter,
                                    normalize_number_list, renderer, split_tag)


@pytest.mark.parametrize('input,text,tag', [
    ('text', 'text', ''),
    ('text {#tag#}', 'text', 'tag'),
    ('{#tag#} text', 'text', 'tag'),
])
def test_split_tag(input, text, tag):
    assert split_tag(input) == (text, tag)


@pytest.mark.parametrize('kind,number_list,page_index,output', [
    ('header', [1], None, [1]),
    ('header', [1, 2], [3], [3, 2]),
    ('figure', [3], None, [3]),
    ('figure', [3], [4, 2], [4, 2, 3]),
])
def test_normalized_number_list(kind, number_list, page_index, output):
    assert normalize_number_list(kind, number_list, page_index) == output


@pytest.fixture
def source():
    yield """
# header {#H1#}

A text

## header {#H1.1#}

#Fig. figure {#F1#}

## header {#H1.2#}

#figure figure {#F2#}

# header {#H2#}

## header {#H2.1#}

#Table table {#T1#}

A text

#Tab. table {#T2#}

### header {#H2.1.1#}

A text
""".strip()


def test_header_splitter(source):
    for k, splitted in enumerate(header_splitter(source)):
        if isinstance(splitted, str):
            assert splitted == 'A text'
        else:
            assert splitted['title'] == splitted['kind']
            number_list = '[' + splitted['tag'][1:].replace('.', ',') + ']'
            assert splitted['number_list'] == eval(number_list)
        if k == 0:
            assert splitted['cursor'] == 0
        elif k == 2:
            assert splitted['cursor'] == 25
        elif k == 3:
            assert splitted['cursor'] == 55


def test_initialize():
    initialize()


@pytest.fixture
def source_input():
    yield """
# header {#H1#}

A text

## header {#H1.1#}

#Fig. figure {#F1#}

![png](figure1.png)

#Fig. figure {#F2#}

#begin
![png](figure2.png)

![png](figure3.png)
#end

#Tab. table {#T1#}

First Header | Second Header
------------ | -------------
Content Cell | Content Cell
Content Cell | Content Cell
""".strip()


@pytest.fixture
def source_output():
    yield """
# <span id="pheasant-H1">4. header</span>

A text

## <span id="pheasant-H1.1">4.1. header</span>

<div class="pheasant-figure" id="pheasant-F1">
<p><img alt="png" src="figure1.png" /></p>
<p>Figure 4.1. figure</p>
</div>

<div class="pheasant-figure" id="pheasant-F2">
<p><img alt="png" src="figure2.png" /></p>
<p><img alt="png" src="figure3.png" /></p>
<p>Figure 4.2. figure</p>
</div>

<div class="pheasant-table" id="pheasant-T1">
<p>Table 4.1. table</p>
First Header | Second Header
------------ | -------------
Content Cell | Content Cell
Content Cell | Content Cell
</div>
""".strip()


def test_renderer(source_input):
    tag = {}
    for k, splitted in enumerate(renderer(source_input, tag)):
        if k == 0:
            assert splitted == '# <span id="pheasant-H1">1. header</span>'
        elif k == 2:
            assert splitted == '## <span id="pheasant-H1.1">1.1. header</span>'
    for key, value in tag.items():
        assert key == (value['kind'][0].upper() +
                       '.'.join(str(i) for i in value['number_list']))

    tag = {}
    for k, splitted in enumerate(renderer(source_input, tag,
                                          page_index=[2, 3])):
        if k == 0:
            assert splitted == '# <span id="pheasant-H1">2.3. header</span>'
        elif k == 2:
            assert (splitted ==
                    '## <span id="pheasant-H1.1">2.3.1. header</span>')


def test_convert(source_input, source_output):
    output, tag_dictionary = convert(source_input, page_index=[4])
    for lines in zip(output.split('\n'), source_output.split('\n')):
        if lines[0] == '<table>':
            break
        assert lines[0] == lines[1]


@pytest.fixture
def source_tag():
    yield """
# header {#a#}

A text

## header {#b#}

#Fig. figure {#c#}

![png](figure1.png)

#Fig. figure {#d#}

![png](figure2.png)

""".strip()


def test_tag(source_tag):
    source, tag = convert(source_tag)
    assert tag['a'] == {'kind': 'header', 'number_list': [1],
                        'id': 'pheasant-a'}
    assert tag['b'] == {'kind': 'header', 'number_list': [1, 1],
                        'id': 'pheasant-b'}
    assert tag['c'] == {'kind': 'figure', 'number_list': [1],
                        'id': 'pheasant-c'}
    assert tag['d'] == {'kind': 'figure', 'number_list': [2],
                        'id': 'pheasant-d'}
    source, tag = convert(source_tag, page_index=[5])
    assert tag['a'] == {'kind': 'header', 'number_list': [5],
                        'id': 'pheasant-a'}
    assert tag['b'] == {'kind': 'header', 'number_list': [5, 1],
                        'id': 'pheasant-b'}
    assert tag['c'] == {'kind': 'figure', 'number_list': [5, 1],
                        'id': 'pheasant-c'}
    assert tag['d'] == {'kind': 'figure', 'number_list': [5, 2],
                        'id': 'pheasant-d'}

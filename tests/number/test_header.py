import pytest
from pheasant.number.header import (convert, header_splitter, renderer,
                                    split_tag, number_list)


@pytest.mark.parametrize('input,text,tag', [
    ('text', 'text', ''),
    ('text {tag}', 'text', 'tag'),
    ('{tag} text', 'text', 'tag'),
])
def test_split_tag(input, text, tag):
    assert split_tag(input) == (text, tag)


@pytest.mark.parametrize('name,number,page_index,output', [
    ('header', [1], None, [1]),
    ('header', [1, 2], [3], [3, 2]),
    ('figure', [3], None, [3]),
    ('figure', [3], [4, 2], [4, 2, 3]),
])
def test_number_list(name, number, page_index, output):
    assert number_list(name, number, page_index) == output


@pytest.fixture
def source():
    yield """
# header {H1}

A Text

## header {H1.1}

#Fig. figure {F1}

## header {H1.2}

#figure figure {F2}

# header {H2}

## header {H2.1}

#Table table {T1}

A Text

#Tab. table {T2}

### header {H2.1.1}

A Text
""".strip()


def test_header_splitter(source):
    for k, splitted in enumerate(header_splitter(source)):
        if isinstance(splitted, str):
            assert splitted == 'A Text'
        else:
            assert splitted['title'] == splitted['name']
            number = '[' + splitted['tag'][1:].replace('.', ',') + ']'
            assert splitted['number'] == eval(number)
        if k == 0:
            assert splitted['cursor'] == 0
        elif k == 2:
            assert splitted['cursor'] == 23
        elif k == 3:
            assert splitted['cursor'] == 51


@pytest.fixture
def source_input():
    yield """
# header {H1}

A Text

## header {H1.1}

#Fig. figure {F1}

![png](figure1.png)

#Fig. figure {F2}

![png](figure2.png)

#Tab. table {T1}

First Header | Second Header
------------ | -------------
Content Cell | Content Cell
Content Cell | Content Cell
""".strip()


@pytest.fixture
def source_output():
    yield """
# 4. header

A Text

## 4.1. header

<div class="pheasant-figure">
<p><img alt="png" src="figure1.png" /></p>
<p>Figure 4.1. figure</p>
</div>

<div class="pheasant-figure">
<p><img alt="png" src="figure2.png" /></p>
<p>Figure 4.2. figure</p>
</div>

<div class="pheasant-table">
<p>Table 4.1. table</p>
First Header | Second Header
------------ | -------------
Content Cell | Content Cell
Content Cell | Content Cell
</div>
""".strip()


def test_renderer(source_input):
    tag_dictionary = {}
    for k, splitted in enumerate(renderer(source_input, tag_dictionary)):
        if k == 0:
            assert splitted == '# 1. header'
        elif k == 2:
            assert splitted == '## 1.1. header'
    for key, value in tag_dictionary.items():
        assert key == value[0][0].upper() + '.'.join(str(i) for i in value[1])

    tag_dictionary = {}
    for k, splitted in enumerate(renderer(source_input, tag_dictionary,
                                          page_index=[2, 3])):
        if k == 0:
            assert splitted == '## 2.3. header'
        elif k == 2:
            assert splitted == '### 2.3.1. header'


def test_convert(source_input, source_output):
    output, tag_dictionary = convert(source_input, page_index=[4])
    for lines in zip(output.split('\n'), source_output.split('\n')):
        if lines[0] == '<table>':
            break
        assert lines[0] == lines[1]

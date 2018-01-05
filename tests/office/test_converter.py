import pytest
from pheasant.config import config as pheasant_config
from pheasant.office.converter import office_object_splitter, exporter, convert


@pytest.fixture
def source():
    yield """
Text ![alt](powerpoint.pptx#Group1) Text

![alt](workbook.xlsx#Chart1) Text""".strip()


def test_office_object_splitter(source):
    for k, splitted in enumerate(office_object_splitter(source)):
        if k == 0:
            assert splitted == 'Text '
        elif k == 1:
            assert splitted['alt'] == 'alt'
            assert splitted['path'] == 'powerpoint.pptx'
            assert splitted['tag'] == 'Group1'
        elif k == 2:
            assert splitted == ' Text\n\n'
        elif k == 3:
            assert splitted['alt'] == 'alt'
            assert splitted['path'] == 'workbook.xlsx'
            assert splitted['tag'] == 'Chart1'
        if k == 4:
            assert splitted == ' Text'


def test_exporter(source_file, root):
    splitter = exporter(source_file, root)
    assert next(splitter) == 'Text\n\n'
    assert next(splitter).startswith('![png](data:image/png;base64,iVB')
    assert next(splitter) == '\n\nText\n'


def test_convert(source_file):
    pheasant_config['source_file'] = source_file
    source = convert(source_file)
    splitted = source.split('\n\n')
    assert splitted[0] == 'Text'
    assert splitted[1].startswith('![png](data:image/png;base64,iVB')
    assert splitted[2] == 'Text\n'

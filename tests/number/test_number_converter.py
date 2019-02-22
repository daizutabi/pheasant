from pheasant.number.config import config
from pheasant.number.converter import convert


def test_convert():
    assert convert('## header') == '## 1 header'
    answer = '\n'.join([
        '<div class="pheasant-number-table">',
        '<p>Table 1 header</p>',
        '<p>abc</p>', '</div>'])
    convert('#Table header\nabc\n\n') == answer
    config['level'] = 0
    answer = '## <span id="pheasant-number-tag">1.1 header</span>'
    assert convert('## header {#tag#}') == answer

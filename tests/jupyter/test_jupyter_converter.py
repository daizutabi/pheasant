from pheasant.jupyter.config import config
from pheasant.jupyter.converter import code_runner, initialize, reload_modules


def test_code_runner():
    initialize()
    source = ('a\n\n```python\na = 5\na\n```\n\n'
              '{{2*a}}<!-- break -->\n\n'
              'b')
    for k, output in enumerate(code_runner(source)):
        if k == 0:
            assert output == 'a\n\n'
        if k == 1:
            assert output.startswith('```python .pheasant-fenced-code')
        if k == 2:
            assert output == '\n10'
    assert k == 2

    source = '```python inline\na = 5\n{{3*a}}\n```\n'

    for k, output in enumerate(code_runner(source)):
        if k == 0:
            assert output == '15\n\n'
    assert k == 0


def test_reload_modules():
    config['import_modules'] = ['pandas']
    assert reload_modules() is None

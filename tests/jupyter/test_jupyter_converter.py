import nbformat

from pheasant.jupyter.client import run_cell
from pheasant.jupyter.converter import (cell_runner, initialize,
                                        reload_modules, set_config)


def test_cell_runner():
    initialize()
    source = ('a\n\n```python\na = 5\na\n```\n\n'
              '{{2*a}}<!-- break -->\n\n'
              'b')
    for k, output in enumerate(cell_runner(source)):
        if k == 0:
            assert output == 'a\n\n'
        if k == 1:
            assert output.startswith('```python .pheasant-markdown')
        if k == 2:
            assert output == '\n10'
    assert k == 2

    source = '```python inline\na = 5\n{{3*a}}\n```\n'

    for k, output in enumerate(cell_runner(source)):
        if k == 0:
            assert output == '15\n\n'
    assert k == 0


def test_set_config():
    set_config(['timeout=1000', 'holoviews_backend=matplotlib'])
    cell = nbformat.v4.new_code_cell('config')
    run_cell(cell)
    config = eval(cell['outputs'][0]['data']['text/plain'])
    assert config['timeout'] == 1000
    assert config['holoviews_backend'] == 'matplotlib'

    set_config(['timeout=600', 'holoviews_backend=bokeh'])  # revert


def test_reload_modules():
    assert reload_modules() is None

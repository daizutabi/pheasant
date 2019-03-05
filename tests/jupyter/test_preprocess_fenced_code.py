from pheasant.jupyter.client import run_cell
from pheasant.jupyter.converter import initialize
from pheasant.jupyter.preprocess import preprocess_fenced_code


def test_initialize():
    initialize()
    cell = run_cell('import matplotlib.pyplot as plt')
    assert cell.outputs == []


def test_preprocess_fenced_code():
    source = '{{plt.plot([1, 2])}}\n'
    output = preprocess_fenced_code(source)
    assert output == ('pheasant.jupyter.display(plt.plot'
                      '([1, 2]), output="markdown")\n')


def test_preprocess_fenced_code_with_asign():
    source = 'a = {{plt.plot([1, 2])}}\n'
    output = preprocess_fenced_code(source)
    assert output == ('a = pheasant.jupyter.display(plt.plot'
                      '([1, 2]), output="markdown")\n')


def test_preprocess_fenced_code_html():
    source = '{{^plt.plot([1, 2])}}\n'
    output = preprocess_fenced_code(source)
    assert output == ('pheasant.jupyter.display(plt.plot'
                      '([1, 2]), output="html")\n')


def test_preprocess_fenced_code_with_semicolon():
    source = '{{plt.plot([1, 2]);plt.gcf()}}\n'
    output = preprocess_fenced_code(source)
    assert output == ('pheasant.jupyter.display(_pheasant_dummy, '
                      'output="markdown")\n')
    cell = run_cell('_pheasant_dummy')
    assert len(cell.outputs) == 1
    data = cell.outputs[0]['data']
    assert data['text/plain'].startswith('<Figure size ')
    assert data['image/png'].endswith('buIiAf9H7r88xa5EGEMAAAAAElFTkSuQmCC\n')

    cell = run_cell(output)
    assert len(cell.outputs) == 1
    output = cell.outputs[0]
    assert list(output['data'].keys()) == ['text/plain']
    assert output['data']['text/plain'].startswith("'![png]")


def test_run_preprocess_fenced_code_with_for_loop():
    source = ('a = []\nfor k in [1, 3]:\n'
              '    plt.plot([1, k])\n'
              '    a.append({{plt.gcf()}})\n')
    output = preprocess_fenced_code(source)
    assert output.endswith('.jupyter.display(plt.gcf(), output="markdown"))\n')
    cell = run_cell(output)
    assert len(cell.outputs) == 1
    data = cell.outputs[0]['data']
    assert data['text/plain'].startswith('<Figure size ')
    assert data['image/png'].endswith('RNLM/wdlA/DMIoRE0QAAAABJRU5ErkJggg==\n')
    cell = run_cell('a')
    assert len(cell.outputs) == 1
    output = cell.outputs[0]
    assert list(output['data'].keys()) == ['text/plain']
    a = eval(output['data']['text/plain'])
    assert isinstance(a, list)
    assert a[0][-20:] == 'IPFAAAAAElFTkSuQmCC)'
    assert a[1][-20:] == 'QAAAABJRU5ErkJggg==)'

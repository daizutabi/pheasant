from pheasant.jupyter.client import run_cell
from pheasant.jupyter.converter import convert, initialize


def test_initialize():
    initialize()
    cell = run_cell('import matplotlib.pyplot as plt')
    assert cell.outputs == []


def test_simple_inline_fenced_code():
    source = '```python inline\n{{plt.plot([1, 2])}}\n```\n'
    output = convert(source)
    assert output.startswith('![png](data:image/png;base64,iVBORw0KGgo')


def test_asigned_inline_fenced_code():
    source = '```python inline\na={{plt.plot([1, 2])}}\n```\n'
    output = convert(source)
    assert output.startswith('![png](data:image/png;base64,iVBORw0KGgo')
    cell = run_cell('a')
    data = cell.outputs[0]['data']
    assert list(data.keys()) == ['text/plain']
    assert data['text/plain'].startswith("'[&lt;matplotlib.lines.Line2D ")

    source = '```python inline\na={{plt.plot([1, 2]);plt.gca()}}\n```\n'
    output = convert(source)
    assert output == '\n\n'
    cell = run_cell('a')
    data = cell.outputs[0]['data']
    assert list(data.keys()) == ['text/plain']
    assert data['text/plain'].startswith("'![png](data:image/png;base64,")

    source = '```python inline\nplt.plot([1, 2]);a = {{plt.gca()}}\n```\n'
    output = convert(source)
    assert output.startswith('![png](data:image/png;base64,iVBORw0KGgo')
    cell = run_cell('a')
    data = cell.outputs[0]['data']
    assert list(data.keys()) == ['text/plain']
    assert data['text/plain'].startswith("'![png](data:image/png;base64,")

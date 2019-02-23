import nbformat
from pheasant.jupyter.renderer import pheasant_options

def test_pheasant_options():
    cell = nbformat.v4.new_code_cell('a = 1')
    assert pheasant_options(cell) == []
    cell.metadata['pheasant'] = {'options': [1, 2, 3]}
    assert pheasant_options(cell) == [1, 2, 3]

import pytest
from pheasant.jupyter.preprocess import evaluate_markdown
from pheasant.jupyter.converter import initialize


@pytest.mark.parametrize('source,output',
                         [('text', 'text'), ('1{{a=1}}2', '12'),
                          ('a{{a}}b', 'a1b'), ('#{{2*a}}!', '#2!'),
                          ('-{{#a}}-', '-{{a}}-'),
                          ('a{{^a}}b', 'a<p>1</p>b')])
def test_evaluate_markdown(source, output):
    initialize()
    assert evaluate_markdown(source) == output

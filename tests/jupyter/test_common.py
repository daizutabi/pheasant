import pytest
from pheasant.jupyter.common import evaluate_markdown


@pytest.mark.parametrize('source,output',
                         [('text', 'text'), ('1{{a=1}}2', '12'),
                          ('a{{a}}b', 'a1b'), ('#{{2*a}}!', '#2!'),
                          ('-{{#a}}-', '-{{a}}-')])
def test_evaluate_markdown(source, output):
    kernel_name = 'python3'
    assert evaluate_markdown(source, kernel_name) == output

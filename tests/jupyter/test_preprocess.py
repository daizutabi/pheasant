import pytest
from pheasant.jupyter.preprocess import preprocess_markdown
from pheasant.jupyter.converter import initialize
from pheasant.jupyter.config import config


def test_inline_pattern():
    assert config['inline_pattern'] == r'\{\{(.+?)\}\}'


@pytest.mark.parametrize('source,output',
                         [('text', 'text'), ('1{{a=1}}2', '12'),
                          ('a{{a}}b', 'a1b'), ('#{{2*a}}!', '#2!'),
                          ('-{{#a}}-', '-{{a}}-'),
                          ('a{{^a}}b', 'a<p>1</p>b'),
                          ('a{{b=10;a+b}}b', 'a11b'),
                          ])
def test_evaluate_markdown(source, output):
    initialize()
    assert preprocess_markdown(source) == output


def test_evaluate_markdown_display():
    initialize()
    output = preprocess_markdown('a{{x=1}}{{!x}}')
    assert output == 'a\n\n```display .pheasant-jupyter-display\n1\n```\n\n'

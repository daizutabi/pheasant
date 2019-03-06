import pytest
from bokeh.resources import CDN

from pheasant.config import config as pheasant_config
from pheasant.jupyter.client import execute
from pheasant.jupyter.config import config
from pheasant.jupyter.converter import initialize
from pheasant.jupyter.preprocess import move_from_header, preprocess_markdown


def test_inline_pattern():
    assert config['inline_pattern'] == r'\{\{(.+?)\}\}'


def test_intialize():
    assert initialize() is None


@pytest.mark.parametrize('source,output',
                         [('text', 'text'), ('1{{a=1}}2', '12'),
                          ('a{{a}}b', 'a1b'), ('${{2*a}}!', '$2!'),
                          ('-{{#a}}-', '-{{a}}-'),
                          ('a{{^a}}b', 'a<p>1</p>b'),
                          ('a{{b=10;a+b}}b', 'a11b'),
                          ('x{{a;b;3*b-a}}y', 'x29y'),
                          ])
def test_evaluate_markdown(source, output):
    assert preprocess_markdown(source) == output


def test_evaluate_markdown_display():
    output = preprocess_markdown('a{{x=1}}{{!x}}')
    assert output == 'a\n\n```display .pheasant-jupyter-display\n1\n```\n\n'


def test_update_extra_resources_for_bokeh():
    pheasant_config['source_file'] = None  # for next test
    code = '\n'.join([
        "from bokeh.plotting import figure",
        "p = figure(title='Test', width=200, height=200)",
        "p.xaxis.axis_label = 'Petal Length'",
        "p.yaxis.axis_label = 'Petal Width'",
        "p.circle([1, 2, 3], [4, 5, 6])",
        "p"
    ])
    data = execute(code)[0]['data']
    assert data['text/plain'].startswith("Figure(id='")
    assert data['text/html'].startswith('<div style="display: table;">')
    assert preprocess_markdown('{{p}}').startswith('\n<script type="text/ja')

    pheasant_config['source_file'] = 'example.md'  # for next test
    preprocess_markdown('{{p}}')


@pytest.mark.parametrize('key, values', [
    ('extra_css', CDN.css_files),
    ('extra_raw_css', []),
    ('extra_javascript', CDN.js_files),
    ('extra_raw_javascript', []),
])
def test_update_extra_resources_for_bokeh_config(key, values):
    assert pheasant_config[key] == values


@pytest.mark.parametrize('key, values', [
    ('extra_css', CDN.css_files),
    ('extra_raw_css', []),
    ('extra_javascript', CDN.js_files),
    ('extra_raw_javascript', []),
])
def test_update_extra_resources_for_page(key, values):
    assert pheasant_config['extra_resources']['example.md'][key] == values


def test_update_extra_resources_for_holoviews():
    pheasant_config['source_file'] = None  # for next test
    code = '\n'.join([
        "import holoviews as hv",
        "import numpy as np",
        "frequencies = [0.5, 0.75, 1.0, 1.25]",
        "def sine_curve(phase, freq):",
        "    xvals = [0.1 * i for i in range(100)]",
        "    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))",
        "curve_dict = {f: sine_curve(0, f) for f in frequencies}",
        "hmap = hv.HoloMap(curve_dict, kdims='frequency')",
        "hmap"])
    data = execute(code)[0]['data']
    plain = ':HoloMap   [frequency]\n   :Curve   [x]   (y)'
    assert data['text/plain'] == plain

    text = preprocess_markdown('{{hmap}}')[:40]
    assert text == '<div class="hololayout row row-fluid">\n '

    extra_css = pheasant_config['extra_css']
    assert len(extra_css) == 5
    assert extra_css[:3] == CDN.css_files
    extra_javascript = pheasant_config['extra_javascript']
    assert len(extra_javascript) == 8
    assert extra_javascript[:4] == CDN.js_files


@pytest.mark.parametrize('index, host, name', [
    (3, 'maxcdn.bootstrapcdn.com', 'bootstrap.min.css'),
    (4, 'code.jquery.com', 'jquery-ui.css'),
])
def test_extra_css_outside_bokeh(index, host, name):
    split = pheasant_config['extra_css'][index].split('/')
    assert split[2] == host
    assert split[-1] == name


def test_extra_raw_css():
    extra = pheasant_config['extra_raw_css']
    assert len(extra) == 1


@pytest.mark.parametrize('index, host, name', [
    (4, 'code.jquery.com', None),
    (5, 'code.jquery.com', 'jquery-ui.min.js'),
    (6, 'cdnjs.cloudflare.com', 'require.min.js'),
    (7, 'cdnjs.cloudflare.com', 'underscore-min.js'),
])
def test_extra_javascript_outside_bokeh(index, host, name):
    split = pheasant_config['extra_javascript'][index].split('/')
    assert split[2] == host
    if name:
        assert split[-1] == name


def test_extra_raw_javascript():
    extra = pheasant_config['extra_raw_javascript']
    assert len(extra) == 2
    assert extra[0][:40] == 'function HoloViewsWidget() {\n}\n\nHoloView'
    assert extra[0][-40:] == 'kehScrubberWidget = BokehScrubberWidget\n'


def test_move_from_header():
    source = 'dummy\n#header {{inline}} title.\n\n#Fig title. {{fig}}\n'
    output = move_from_header(source)
    answer = ('dummy\n#header title.\n<!-- begin -->\n{{inline}}\n'
              '<!-- end -->\n\n#Fig title.\n<!-- begin -->\n'
              '{{fig}}\n<!-- end -->\n')
    assert output == answer

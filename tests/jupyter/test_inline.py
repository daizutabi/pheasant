import matplotlib.pyplot as plt
import pandas as pd
from bokeh.plotting import figure
from pheasant.jupyter.inline import convert_inline


def test_convert_inline():
    a = 1
    assert convert_inline(a) == '1'
    assert convert_inline(a, output='html') == '<p>1</p>'

    a = '<a>'
    assert convert_inline(a) == '<a>'
    assert convert_inline(a, output='html') == '<p><a></p>'

    a = [1, '<a>']
    assert convert_inline(a) == '[1, &#x27;&lt;a&gt;&#x27;]'
    assert convert_inline(a, output='html') == "<p>[1, '<a>']</p>"

    df = pd.DataFrame([[1, 2], [3, 4]], columns=list('ab'))
    assert convert_inline(df).startswith('<table')
    assert convert_inline(df, output='html').startswith('<table')

    fig = plt.figure(figsize=(2, 2))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2])
    assert convert_inline(fig).startswith('![png](data:image/png;base64,iVBOR')
    assert convert_inline(fig, output='html').startswith(
        '<img alt="png" src="data:image/png;base64,iVBOR')
    assert convert_inline(ax).startswith('![png](data:image/png;base64,iVBOR')

    plot = figure(plot_width=250, plot_height=250)
    plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
    assert convert_inline(plot).strip().startswith(
        '<script type="text/javascript">')
    assert convert_inline(plot, output='html').strip().startswith(
        '<script type="text/javascript">')

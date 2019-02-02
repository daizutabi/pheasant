import
import matplotlib.pyplot as plt
import pandas as pd
from bokeh.plotting import figure
from pheasant.jupyter.display import display


def test_display():
    a = 1
    assert display(a) == '1'
    assert display(a, output='html') == '<p>1</p>'

    a = '<a>'
    assert display(a) == '<a>'
    assert display(a, output='html') == '<p><a></p>'

    a = [1, '<a>']
    assert display(a) == '[1, &#x27;&lt;a&gt;&#x27;]'
    assert display(a, output='html') == "<p>[1, '<a>']</p>"

    df = pd.DataFrame([[1, 2], [3, 4]], columns=list('ab'))
    assert display(df).startswith('<table')
    assert display(df, output='html').startswith('<table')

    fig = plt.figure(figsize=(2, 2))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot([1, 2])
    assert display(fig).startswith('![png](data:image/png;base64,iVBOR')
    assert display(
        fig, output='html').startswith(
            '<img alt="png" src="data:image/png;base64,iVBOR')
    assert display(ax).startswith('![png](data:image/png;base64,iVBOR')

    plot = figure(plot_width=250, plot_height=250)
    plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
    assert display(plot).strip().startswith(
        '<script type="text/javascript">')
    assert display(
        plot,
        output='html').strip().startswith('<script type="text/javascript">')

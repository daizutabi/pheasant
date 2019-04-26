# Image Processing

In this section, we study how to embed images created by [Matplotlib](https://matplotlib.org/), [Bokeh](https://bokeh.pydata.org/en/latest/), [HoloViews](https://holoviews.org/), and [Altair](https://altair-viz.github.io/) libraries.

## Matplotlib

First, `figsize` of `figure` is set to `[2, 1.6]` to show small figures for saving space.

```python
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['figure.figsize'] = [2, 1.6]
```

A call of `plt.plot` generates a standard plain text output (a list of `Line` object in this example) and a PNG image as display data:

```python
plt.plot([1, 2, 4], marker='o')
```

If you want to hide the input source and the plain text output, you can use a `inline` option to show just the display data such as an image or HTML:

~~~copy
```python inline
plt.plot([4, 2, 3], marker='o')
```
~~~

**"Inline code"** is useful to display a plot in shorthand notation. `{{#plt.plot([1, 2, 4])}}` generates:

{{plt.plot([1, 2, 4])}}

Note that the plain text output (`[<matplotlib.lines...]`) does not displayed if the inline code generates display data.

## Bokeh

You can embed [Bokeh](https://bokeh.pydata.org/en/latest/)'s plots into MkDocs HTML documents. Following [User Guide "Embedding Plots and Apps"](https://bokeh.pydata.org/en/latest/docs/user_guide/embed.html) from the official Bokeh documents, Pheasant automatically adds extra stylesheet and javascript in HTML source. You don't need to configure `extra_css` and `extra_javascript` in your `mkdocs.yml` manually.

In order to embed plots in your document, `bokeh.embed.components` function can be used. This function returns `<script>`  and `<div>` tags in HTML format. For example:

```python
from bokeh.plotting import figure
from bokeh.embed import components

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 3, 3, 2, 4], size=10)
script, div = components(plot)
print('[script]:', script[:140].strip(), '...')
print('[div]:', div[:40].strip(), '...')
```

Pheasant uses this functionality inside automatically. You can get a Bokeh plot just write `{{#plot}}`:

{{plot}}

## HoloViews

HoloViews provides an explorable multi-dimensional dictionary of HoloViews objects called [HoloMap](https://holoviews.org/reference/containers/bokeh/HoloMap.html). Pheasant can also embed this interactive object in your MkDocs Documents as well as other HoloViews objects.

First, a normal HoloViews object.

```python
import holoviews as hv
hv.Curve(([1, 2, 4], [2, 3, 4]))
```

Showing a HoloMap is straightforward. From HoloViews's official documents,

```python
import numpy as np
frequencies = [0.5, 0.75, 1.0, 1.25]

def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

curve_dict = {f:sine_curve(0,f) for f in frequencies}
hv.HoloMap(curve_dict, kdims='frequency')
```

```python
phases = [0, np.pi/2, np.pi, 3*np.pi/2]
curve_dict_2D = {(p,f):sine_curve(p,f) for p in phases for f in frequencies}
hv.HoloMap(curve_dict_2D, kdims=['phase', 'frequency'])
```

## Altair

From official [Example Gallery](https://altair-viz.github.io/gallery/index.html)

### ##Simple Bar Chart

```python
import altair as alt
import pandas as pd

source = pd.DataFrame({
    'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    'b': [28, 55, 43, 91, 81, 53, 19, 87, 52]
})

alt.Chart(source).mark_bar().encode(
    x='a',
    y='b'
)
```


### Multi-Line Tooltip

```python
import altair as alt
import pandas as pd
import numpy as np

np.random.seed(42)
source = pd.DataFrame(np.cumsum(np.random.randn(100, 3), 0).round(2),
                    columns=['A', 'B', 'C'], index=pd.RangeIndex(100, name='x'))
source = source.reset_index().melt('x', var_name='category', value_name='y')

# Create a selection that chooses the nearest point & selects based on x-value
nearest = alt.selection(type='single', nearest=True, on='mouseover',
                        fields=['x'], empty='none')

# The basic line
line = alt.Chart().mark_line(interpolate='basis').encode(
    x='x:Q',
    y='y:Q',
    color='category:N'
)

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
selectors = alt.Chart().mark_point().encode(
    x='x:Q',
    opacity=alt.value(0),
).add_selection(
    nearest
)

# Draw points on the line, and highlight based on selection
points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

# Draw text labels near the points, and highlight based on selection
text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'y:Q', alt.value(' '))
)

# Draw a rule at the location of the selection
rules = alt.Chart().mark_rule(color='gray').encode(
    x='x:Q',
).transform_filter(
    nearest
)

# Put the five layers into a chart and bind the data
alt.layer(line, selectors, points, rules, text,
          data=source, width=600, height=300)
```

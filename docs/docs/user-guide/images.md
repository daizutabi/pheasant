# Image Processing

In this section, we study how to embed images created by [Matplotlib](https://matplotlib.org/), [Bokeh](https://bokeh.pydata.org/en/latest/), and [HoloViews](https://holoviews.org/) libraries.

## Matplotlib

First, `figsize` of `figure` is set to `[2, 1.6]` to show small figures for saving space.

```python
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rcParams['figure.figsize'] = [2, 1.6]
```

A call of `plt.plot` generates a standard plain text output (a list of `Line` object in this example) and a PNG image as display data:

```python
plt.plot([1, 3, 5], marker='o')
```

If you want to hide the input source and the plain text output, you can use a `display` option to show just the display data such as an image or HTML:

~~~copy
```python display
plt.plot([4, 2, 3], marker='o')
```
~~~

**"Inline code"** is useful to display a plot in shorthand notation. `{{#plt.plot([1, 2, 4])}}` generates:

{{plt.plot([1, 2, 4])}}

Note that the plain text output (`[<matplotlib.lines...]`) does not displayed if the inline code generates display data.

An inline code statement (`{{#<expr>}}`) can be written in a fenced code block. In this case, the expression in the statement is evaluated dynamically during the evaluation of the fenced code block.

In the next example, two plots are overlayed. `axes[0]` and `axes[1]` refer to the same image object.

```python
axes = []
for k, color in enumerate(['red', 'blue']):
  plt.plot([1, k + 3], color)
  axes.append(plt.gca())
axes
```

You can use the inline code to get different images at the every evaluation time while the iteration is going. You have to call `plt.cla()` method to continuously clear the previous plot.

~~~copy
```python hide inline
axes = []
for k, color in enumerate(['red', 'blue']):
    plt.plot([0, k + 3], color)
    axes.append({{plt.gca()}})
    plt.cla()
```
~~~

Here, `hide` option disables the output of plot from the fenced code block, which we don't need now.

Check the type of elements of the variable `axes`.

```python
[type(ax) for ax in axes]
```

They are `str` objects, not any Matplotlib objects. Actually, their content is a base64-encoded markdown image source:

```python
axes[0][:50]
```

Thanks to this Pheasant feature, you can put images anywhere. For example, in a table:

~~~~copy
#Tab A Markdown table with Matplotlib plot
~~~
|Red         |Blue       |
|------------|-----------|
|{{axes[0]}} |{{axes[1]}}|
~~~
~~~~

Herer, a fenced code is required because `{{#axes[0]}}` and `{{#axes[1]}}` are not normal Markdown sources.

If you prefer a Pandas DataFrame, HTML-type inline code can be used with `{{#^` and `}}` which return an IPython HTML object. So you can use the `data` attribute to get a HTML string.

~~~copy
```python hide inline
axes = []
for k, color in enumerate(['red', 'blue']):
    plt.plot([0, k + 3], color)
    axes.append({{^plt.gca()}}.data)
    plt.cla()
```
~~~


Then,

~~~copy
#Tab A Pandas DataFrame with a Matplotlib plot
```python display
import pandas as pd
pd.DataFrame([axes], columns=['Red', 'Blue'])
```
~~~

## Bokeh

You can embed [Bokeh](https://bokeh.pydata.org/en/latest/)'s plots into MkDocs HTML documents. Following [User Guide "Embedding Plots and Apps"](https://bokeh.pydata.org/en/latest/docs/user_guide/embed.html) from the official Bokeh documents, Pheasant automatically adds extra stylesheet and javascript in HTML source. You don't need to configure `extra_css` and `extra_javascript` in your `mkdocs.yml` manually.

In order to embed plots in your document, `bokeh.embed.components` function can be used. This function returns `<script>`  and `<div>` tags in HTML format. For example:

```python
from bokeh.plotting import figure
from bokeh.embed import components

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 3, 0, 2, 4], size=10)
script, div = components(plot)
print('[script]:', script[:140].strip(), '...')
print('[div]:', div[:40].strip(), '...')
```

Pheasant uses this functionality inside automatically. You can get a Bokeh plot just write `{{#plot}}`:

{{plot}}

## HoloViews

HoloViews provides an explorable multi-dimensional dictionary of HoloViews objects called [HoloMap](https://holoviews.org/reference/containers/bokeh/HoloMap.html). Pheasant can also embed this interactive object in your MkDocs Documents as well as other HoloViews objects.

First, a normal HoloViews object.

~~~copy
```python
import holoviews as hv
curve = hv.Curve(([1, 2, 3], [2, 3, 1]))
curve
```
~~~

```python
type(curve)
```

As you can see, HoloView's `Curve` object doesn't supply any visual representation. To get a HTML source to visualize it, we have to render the object.

```python
renderer = hv.renderer('bokeh')
html = renderer.html(curve)
print(html[:40], '...')
```

Extra assets which should be written in a HTML source to display the image are provided by the `renderer`'s class method: `html_assets()`.

```python
js_html, css_html = renderer.html_assets()
print(js_html.strip()[:50])
```
```python
print(css_html.strip()[:50])
```

The above process to display a HTML image from a HoloViews object can be done by just an inline code like this.

~~~copy
{{curve}}
~~~

Showing a HoloMap is straightforward. From HoloViews's official documents,

```python
import numpy as np
frequencies = [0.5, 0.75, 1.0, 1.25]

def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

curve_dict = {f:sine_curve(0,f) for f in frequencies}
hmap = hv.HoloMap(curve_dict, kdims='frequency')
```

~~~copy
{{hmap}}
~~~

```python
phases = [0, np.pi/2, np.pi, 3*np.pi/2]
curve_dict_2D = {(p,f):sine_curve(p,f) for p in phases for f in frequencies}
hmap = hv.HoloMap(curve_dict_2D, kdims=['phase', 'frequency'])
```

~~~copy
{{hmap}}
~~~

# Image

In this section, we study how to embed images created by Matplotlib and Bokeh libraries.

## Matplotlib

First, `figsize` of `figure` is temporally set to `[2, 1.6]` to show small figures for saving space.

```python
import matplotlib as mpl
figsize = mpl.rcParams['figure.figsize']
mpl.rcParams['figure.figsize'] = [2, 1.6]
```

Normal usage of `plt.plot` generates a standard output (a list of `Line` object in this example) and a PNG image:

```python
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], marker='o')
```

If you want to hide the input source and standard output, you can use a `hide` option which only shows the display data such as an image or html:

~~~
```python hide
plt.plot([4, 2, 3], marker='o')
```
~~~

```python hide
plt.plot([4, 2, 3], marker='o')
```

"Inline code" is useful to display plots in shorthand notation. `{{#plt.plot([1, 2, 4]);plt.gcf()}}` and `{{#plt.plot([5, 2, 1])[0]}}` generates:

{{plt.plot([1, 2, 4]);plt.gcf()}} and {{plt.plot([5, 2, 1])[0]}}

In the first code, the object between `{{#` and `}}` is a `Figure` object of matplotlib. In the second, that is a `Line` object. These objects are automatically converted into a PNG image.

An inline code statement (`{{#<expr>}}`) can be written in a fenced code block. In this case, the expression in the statement is evaluated dynamically during the evaluation of the whole block.

In the next example, two plot is overlayed. `axes[0]` and `axes[1]` are the same image.

```python
axes = []
for k, color in enumerate(['red', 'blue']):
  plt.plot([1, k + 3], color)
  axes.append(plt.gca())
axes
```

You can use the inline statement to get different images at the evaluation.

~~~
```python inline
axes = []
for k, color in enumerate(['red', 'blue']):
    plt.plot([1, k + 3], color)
    axes.append({{plt.gca()}})
axes[0] + axes[1]
```
~~~

```python inline
axes = []
for k, color in enumerate(['red', 'blue']):
    plt.plot([1, k + 3], color)
    axes.append({{plt.gca()}})
axes[0] + axes[1]
```

To clear the `axes` during loop, call `plt.cla()` function.

~~~
```python inline
axes = []
for k, color in enumerate(['red', 'blue']):
    plt.plot([1, k + 3], color)
    axes.append({{plt.gca()}})
    plt.cla()
axes[0] + axes[1]
```
~~~

```python inline
axes = []
for k, color in enumerate(['red', 'blue']):
    plt.plot([1, k + 3], color)
    axes.append({{plt.gca()}})
    plt.cla()
axes[0] + axes[1]
```

Finally, let's set the `figsize` to its original value.

```python
mpl.rcParams['figure.figsize'] = figsize
```

## Bokeh

You can embed plots into MkDocs HTML documents. Following [User Guide "Embedding Plots and Apps"](https://bokeh.pydata.org/en/latest/docs/user_guide/embed.html) from official Bokeh documents, configure your `mkdocs.yml` as below:

```yml
extra_css:
  - https://cdn.pydata.org/bokeh/release/bokeh-0.12.14.min.css
  - https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.14.min.css
  - https://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.14.min.css

extra_javascript:
  - https://cdn.pydata.org/bokeh/release/bokeh-0.12.14.min.js
  - https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.14.min.js
  - https://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.14.min.js
```

Here, `0.12.14` is a version number of Bokeh and you can choose other version number you want to use.

In order to embed a plot in your document, `bokeh.embed.components` function can be used. This function returns `<script>`  and `<div>` tags. For example:

```python
from bokeh.plotting import figure
from bokeh.embed import components

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
script, div = components(plot)
print(script[:132] + '...\n', div)
```

These `<script>`  and `<div>` tags are used in inline code of `{{#script}}{{#div}}` to get a plot as shown below:

`{{#script}}{{#div}}`
{{script}}{{div}}

A shortcut to this functionality is prepared.

`{{#plot}}`

{{plot}}

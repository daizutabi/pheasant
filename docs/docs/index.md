# Pheasant

Welcome to Pheasant! In this section, overview and some interesting features of Pheasant are presented.

## Overview

Pheasant is a Markdown converter which is designed to work with [MkDocs](http://www.mkdocs.org/) as a plugin.

Highlights include:

+ Auto generation of outputs for a fenced code block or inline code in Markdown source using [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/). The code language is not restricted to Python.
+ Auto numbering of headers, figures, and tables, and etc. Numbered objects can be linked from other Markdown sources.

## Installation

You can install Pheasant from PyPI.

~~~bash
$ pip install pheasant
~~~

If you use Pheasant as a plugin of MkDocs, you also need to install it.

~~~bash
$ pip install mkdocs
~~~

Then, in your `mkdocs.yml`, add lines below to register Pheasant as a MkDocs plugin and its theme based on [Read *the* Docs theme](https://sphinx-rtd-theme.readthedocs.io/en/stable/):

~~~yaml
theme: rtd-pheasant

plugins:
  - pheasant
~~~

## Getting Started

### Auto generation of the executed outputs with Jupyter client

A markdown source below:

~~~
```python
print(1)
```
~~~

is converted into:

~~~
```python
print(1)
```

```python
1
```
~~~

after execution of `print` function via [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/) and finally rendered as:

```python
print(1)
```

### Inline code embeded in a Markdown source

**"Inline code"** is a powerful feature of Pheasant. Any python codes surrounded by `{{#` and `}}` are executed and the result remains there. For example, `{{#3*5}}` becomes {{3*5}}. Variables can be assigned in an inline code like this: `{{#name='Pheasant'}}`{{name='Pheasant'}}. Then, `"I'm {{#name}}."` becomes "I'm {{name}}." Note that an inline code without outputs does not shown after execution.

### Visualization

Pheasant supports various output formats other than standard stream or plain text output. For example, you can create a PNG image using Matplotlib. First, import Matplotlib plotting library.

~~~copy
```python
import matplotlib.pyplot as plt
```
~~~

Then, plot a line.

~~~copy
```python
plt.plot([1, 2])
```
~~~

Executin of the above Markdown source on a Jupyter kernel creates a plain text output as a execute result and a PNG image as display data. You may want to display only the image. You can set `display` option to a fenced code after language description:

~~~
```python display
plt.plot([1, 2])
```
~~~

Note that Matplotlib package has already been imported in the previous code block so that we don't need to import it again here.

Pheasant also supports Bokeh's HTML output.

```python
from bokeh.plotting import figure

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
```

The last line of the above code block returns a `GlyphRenderer` object. To show the bokeh's figure instead of it, we can use an inline code described above:

~~~copy
{{plot}}
~~~

In order to put the figure at the center, we can use inline code as **"display"** mode surrounded by `{{#!` and `}}`.

~~~copy
{{!plot}}
~~~

Furthermore, Pheasant supports HoloViews objects as well as interactive HoloMaps.

~~~copy
```python
import holoviews as hv
curve = hv.Curve(((1, 2), (2, 3)))
```

{{!curve}}
~~~

HoloMap can work as in a Jupyter Notebook.

```python
import numpy as np


def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

frequencies = [0.5, 0.75, 1.0]
curve_dict = {f: sine_curve(0, f) for f in frequencies}
holomap = hv.HoloMap(curve_dict, kdims='Frequency')
```

~~~
{{!holomap}}
~~~

{{!holomap}}


### Auto numbering of headers, figures, tables, *etc*.

As you can see, all of headers are numbered in this document. This numbering has done by Pheasant automatically. In addition, Pheasant can count the number of figures, tables, *etc*. and give the identical number to each object.

You can use a special **"header"** statement for figure, table, *etc*. to number them like below:

~~~copy
#Figure This is a cat. {#cat#}
![jpg](img/cat.jpg)
~~~

Supported numbered headers are shown in the next table:


#Table Supported numbered headers
Type   | Markdown
-------|-------------------------------
Header | # (title)
Figure | #Figure (title), #Fig (title)
Table  | #Table (title), #Tab (title)
Code   | #Code (title)
File   | #File (title)

In the above Markdown source, `{#<tag>#}` is an ID tag for hyperlink described below. Off course, you can use any code to create a figure:

~~~copy
#Fig A Matplotlib figure
```python display
plt.plot([3, 2])
```
~~~

Like figures, tables can be numbered.

~~~copy
#Table A Markdown table
a | b
--|--
0 | 1
2 | 3
~~~

Pandas's DataFarme is useful to create a table programmatically.

~~~copy
#Table A Pandas's DataFrame
```python display
import pandas as pd
pd.DataFrame([[1, 2], [3, 4]], index=list('XY'), columns=list('ab'))
```
~~~

A Markdown source for figures and tables is a source block separated by a blank line from following Markdown source. If a figure or table has blank lines within it, you have to explicitly declare the content range with `<!-- begin -->` and `<!-- end -->` statements.

~~~
#Fig A Bokeh's HTML figure
&lt;!-- begin --&gt;
{{!plot}}
&lt;!-- end --&gt;
~~~

#Fig A Bokeh's HTML figure
<!-- begin -->
{{!plot}}
<!-- end -->

However, Pheasant provides an easy way to number figures, tables, *etc*. regardless of whether they actually have any blank lines or not. Try this:

~~~
#Figure {{curve}} Inline numbering method.
~~~

#Fig Inline numbering method {{curve}}

### Hyperlink

Numbered objects are linked from Markdown source using `{#<tag>#}`:

~~~markdown
For example, go to Fig. {#cat#}
~~~

For example, go to Fig. {#cat#}

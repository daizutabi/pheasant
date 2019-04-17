```python hide run
from pheasant import __version__
```

# Pheasant {{__version__}}

Welcome to Pheasant! In this section, overview and some interesting features of Pheasant are presented.

## Overview

Pheasant is a Markdown converter which is designed to work with [MkDocs](http://www.mkdocs.org/) as a plugin.

Highlights include:

+ Auto generation of outputs for a fenced code block or inline code in Markdown source using [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/). The code language is not restricted to Python.
+ Auto numbering of headers, figures, and tables, and etc. Numbered objects can be linked from other Markdown sources.

## Installation

You can install Pheasant from PyPI.

~~~bash terminal
$ pip install pheasant
~~~

If you use Pheasant as a plugin of MkDocs, you also need to install it.

~~~bash terminal
$ pip install mkdocs
~~~

In your `mkdocs.yml`, add lines below to register Pheasant as a MkDocs plugin.

~~~yaml file
plugins:
  - pheasant
~~~

## Getting Started

### Auto generation of the executed outputs with Jupyter client

In a markdown fenced code below,

~~~
```python
print(1)
```
~~~

a `print` function is executed via [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/) and converted into HTML source:

~~~html
<div class="input"><pre><code class="python">print(1)</code></pre></div>
<div class="stdout"><pre><code class="text">1</code></pre></div>
~~~

Then, finally rendered as:

```python
print(1)
```

Other language code can be executed if a kernel for the language has been installed. For example,

~~~
```javascript
console.log("Hello Javascript")
```
~~~

You can check the kernel name and its total execution count during the conversion process at the right side of input cells.

Mapping a language to kernel names can be obtained as a  dictionary by `find_kernel_names` function :

```python
from pheasant.renderers.jupyter.client import find_kernel_names
find_kernel_names()
```

### Inline code embeded in a Markdown source

**"Inline code"** is a powerful feature of Pheasant. Any python codes surrounded by `{{#` and `}}` are automatically executed and the result remains there. For example, `{{#3*5}}` becomes {{3*5}}. Variables can be assigned in an inline code like this: `{{#name='Pheasant'}}`{{name='Pheasant'}}. Then, `"I'm {{#name}}."` becomes "I'm {{name}}."

### Visualization

Pheasant supports various output formats other than standard stream (`sys.stdout`/`sys.stderr`) or plain text output. For example, you can create a PNG image using Matplotlib. First, import Matplotlib plotting library.

~~~copy
```python
import matplotlib.pyplot as plt
```
~~~

Plot a line.

~~~copy
```python
plt.plot([1, 3])
```
~~~

Executin of the above Markdown source on a Jupyter kernel creates a plain text output as an execute result and a PNG image as display data. You may want to display only the image. You can set `inline` option to a fenced code after language description:

~~~copy
```python inline
plt.plot([1, 2])
```
~~~

Pheasant also supports Bokeh's HTML output.

```python
from bokeh.plotting import figure
plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
plot
```

As well as a fenced code style, we can choose inline code style: `{{#plot}}`

{{plot}}


Furthermore, Pheasant supports HoloViews objects as well as interactive HoloMap.

```python
import holoviews as hv
hv.Curve(((1, 2), (2, 3)))
```

HoloMap can work as in a Jupyter Notebook.

```python
import numpy as np

def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

frequencies = [0.5, 0.75, 1.0]
curve_dict = {f: sine_curve(0, f) for f in frequencies}
hv.HoloMap(curve_dict, kdims='Frequency')
```

Finally, Altair plots from official [Example Gallery](https://altair-viz.github.io/gallery/index.html),

```python
import altair as alt
import pandas as pd

source = pd.DataFrame({
    'a': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
    'b': [30, 55, 43, 91, 81, 53, 19, 87, 52]
})

alt.Chart(source).mark_bar().encode(x='a', y='b')
```

```python
import altair as alt
from vega_datasets import data

source = data.seattle_weather()
brush = alt.selection(type='interval', encodings=['x'])

bars = alt.Chart().mark_bar().encode(
    x='month(date):O',
    y='mean(precipitation):Q',
    opacity=alt.condition(brush, alt.OpacityValue(1), alt.OpacityValue(0.7))
).add_selection(
    brush
)

line = alt.Chart().mark_rule(color='firebrick').encode(
    y='mean(precipitation):Q',
    size=alt.SizeValue(3)
).transform_filter(
    brush
)

alt.layer(bars, line, data=source)
```

### Auto numbering of headers, figures, tables, *etc*.

As you can see, all of headers are numbered in this document. This numbering has done by Pheasant automatically. In addition, Pheasant can count the number of figures, tables, *etc*. and give the identical number to each object.

You can use a special **"header"** statement for figure, table, *etc*. to number them like below:

~~~
#Fig Markdown link for an image can be numbered. {##cat#}
![jpg](img/cat.jpg)
~~~

#Fig Markdown link for an image can be numbered. {#cat#}
![jpg](img/cat.jpg)

Supported numbered headers are shown in Table {#numbered-header#}:

#Tab Supported numbered headers {#numbered-header#}
Type     | Markdown
---------|-------------------------------
Header   | # (title)
Figure   | #Figure (title), #Fig (title)
Table    | #Table (title), #Tab (title)
Equation | #Eq (equation), #Eq* (equation)
[other]  | #[other] (title)

In the above Markdown source, `{##<tag>#}` is an ID tag for hyperlink described below. Off course, you can use any code to create a figure.

~~~~copy
#Figure A Matplotlib figure
```python
plt.plot([2, 4])
```
~~~~

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
```python
import pandas as pd
pd.DataFrame([[1, 2], [3, 4]], index=list('XY'), columns=list('ab'))
```
~~~

A **plain** Markdown source which is not processed by Pheasant has to be separated by a blank line from the following Markdown source which is not a part of the figure or table. If a figure or table has blank lines within it, you have to write the content in a fenced code with tilde (`~~~`).

~~~~copy
#Fig A figure with a blank line
~~~
![jpg](img/cat.jpg)

![jpg](img/cat.jpg)
~~~
~~~~

In addition, Pheasant provides an easy way to number figures, tables, *etc*. regardless of whether they actually have any blank lines or not. Try this:

~~~copy
#Figure {{plot}} Inline numbering method.
~~~

### Hyperlink

Numbered objects are linked from Markdown source using `{##<tag>#}`:

~~~markdown
For example, go to Fig. {##cat#}
~~~

For example, go to Fig. {#cat#}

### Link from a header

You can add external link from section headers.

~~~copy
#### MkDocs (https://www.mkdocs.org/)
~~~

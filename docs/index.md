# Pheasant Documentation

## Overview

Welcome to Pheasant. Pheasant is a Markdown converter which is designed to work with [MkDocs](http://www.mkdocs.org/) as a plugin.

Highlights include:

+ Auto generation of outputs for a fenced code block or inline code in Markdown source using [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/). The code language is not restricted to Python.
+ Auto numbering of headers, figures, tables, and etc. Numbered objects can be linked from other Markdown sources.

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

a `print` function is executed via [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/) and converted into HTML:

~~~html
<div class="input"><pre><code class="python">print(1)</code></pre></div>
<div class="stdout"><pre><code class="nohighlight">1</code></pre></div>
~~~

Then, finally rendered as:

```python
print(1)
```

Other language code can be executed if a kernel for the language has been installed. For example,

~~~copy
```julia
println("Hello, IJulia!")
```
~~~

You can check the kernel name and its total execution time during the conversion process at the right side of an input cell.

Like [Jupyter Notebook](https://jupyter-notebook.readthedocs.io/en/stable/), the last object in a code cell is displayed as the output of the cell.

~~~copy
```python
greeting = 'Hello, Python'
greeting
```
~~~

### Inline code embeded in a Markdown source

**"Inline code"** is a powerful feature of Pheasant. Any executable codes surrounded by `{{#` and `}}` are automatically executed and the codes are replaced with the execution result. For example, `{{#3*4}}` becomes {{3*4}}. Variables can be assigned in an inline code like this: `{{#name='Pheasant'}}`{{name='Pheasant'}}. Then, `"I'm {{#name}}."` becomes "I'm {{name}}."

### Visualization

Pheasant supports various output formats other than the standard stream (`stdout`/`stderr`) or a plain text output. For example, you can create a PNG image using [Matplotlib](https://matplotlib.org/). First, import the Matplotlib plotting library.

~~~copy
```python
import matplotlib.pyplot as plt
```
~~~

Plot a line.

~~~copy
```python
plt.plot([1, 2])
```
~~~

Execution of the above Markdown source on a Jupyter client creates a plain text output as an execute result and a PNG image as display data. You may want to display only the image. You can set `inline` option to a fenced code after a language identifier:

~~~copy
```python inline
plt.plot([1, 3])
```
~~~

Or use an inline code directly: `{{#plt.plot([1, 4])}}` {{plt.plot([1, 4])}}

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
Type     | Markdown (case-insensitive)
---------|-------------------------------
Header   | # (title)
Figure   | #Figure (title), #Fig (title)
Table    | #Table (title), #Tab (title)
Equation | #Eq (equation), #Eq* (equation)
[other]  | #[other] (title)

In the above Markdown source, `{##<tag>#}` is an ID tag for hyperlink described below. Off course, you can use any codes to create a figure.

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

[Pandas](http://pandas.pydata.org/)'s DataFarme is useful to create a table programmatically.

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

In addition, Pheasant provides an easy way to number objects regardless of whether they actually have any blank lines or not. Try this:

~~~copy
#Figure {{plt.plot([1, 5])}} Numbered figure using an inline code.
~~~

### Hyperlink

Numbered objects are linked from Markdown source using `{##<tag>#}`:

~~~markdown
For example, go to Fig. {##cat#}
~~~

For example, go to Fig. {#cat#}

You can add an external link in a header.

~~~copy
#### MkDocs (https://www.mkdocs.org/)
~~~

### Inspect source (Python only)

`inspect` option to get source.

#### Source code in a code cell
~~~copy
```python inspect
def func(x):
    return x + 2

func
```
~~~

#### Source code from file
~~~copy
```python inspect
from pheasant.renderers.jupyter.jupyter import Cell

Cell
```
~~~

#### Inline mode (with custom 'Code' header)

~~~copy
#Code {{ func # inspect }}
~~~

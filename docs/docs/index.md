# Pheasant

## Overview

Pheasant is a Markdown converter which can be used as a plugin for static site generators such as [MkDocs](http://www.mkdocs.org/) or [Pelican](http://docs.getpelican.com/en/stable/). Highlights include:

+ Auto generation of outputs for a fenced code block in Markdown using [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/). The code language is not restricted to Python.
+ Auto numbering of headers, figures, and tables. Numbered objects can be linked in Markdown source.
+ Simple interface to use Pheasant with other site generators.
+ Easy to install any extensions you want to Pheasant.


## How to install

You can install Pheasant from PyPI.

~~~
$ pip install pheasant
~~~

If you use Pheasant as a plugin for MkDocs or Pelican, you also need to instal them.

~~~
$ pip install mkdocs pelican
~~~

## Plugin settings

### MkDocs

In your `mkdocs.yml`, add lines below:

~~~
plugins:
  - pheasant:
      jupyter:
        enabled: True
      number:
        enabled: True
~~~

### Pelican

In your `pelicanconf.py`, add lines below:

~~~
PLUGINS = ['pheasant']
PHEASANT = {'jupyter': {'enabled': True}}
~~~

!!! Note
    Auto numbering feature is not suitable for articles (such as blog) written in Pelican.

## Examples

### Auto generation of outputs with Jupyter client

A markdown soure below:

~~~
```python
print(1)
```
~~~

is converted into:

~~~
```python
>>> print(1)
1
```
~~~

after execution of `print` function and finally the output becomes

```python
print(1)
```

Pheasant supports various output formats other than standard stream. For example, you can create a PNG image from Matplotlib.

~~~
```python
%matplotlib inline
import matplotlib.pyplot as plt
plt.plot([1, 3, 2]);
```
~~~

The above Markdown creates a PNG image:

```python
%matplotlib inline
import matplotlib.pyplot as plt
plt.plot([1, 3, 2]);
```

You may want not to display Python code itself. You can use `hide-input` option after a ```` ```python ```` statement.

~~~
```python hide-input
plt.plot([1, 3, 2]);
```
~~~

This creates only a PNG image without Python code like below:

```python hide-input
plt.plot([1, 3, 2]);
```

Pheasant also supports Bokeh's HTML output.

~~~
```python hide-input
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.io import show
output_notebook()
p = figure(plot_width=250, plot_height=250)
p.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
show(p)
```
~~~

```python hide-input
from bokeh.plotting import figure
from bokeh.io import output_notebook
from bokeh.io import show
output_notebook()
p = figure(plot_width=250, plot_height=250)
p.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
show(p)
```

The language executed in Jupyter is not restricted to Python. For example,
if you install Julia kernel, you can write:

~~~
```julia
x = 2
println(3x)
```
~~~

to get output like below:


```julia
x = 2
println(3x)
```

### Auto numbering of headers, figures, and tables.

As you can see, all of headers are numbered in this document. This is done by Pheasant automatically. In addition, Pheasant can count the number of figures and tables and give the identical number to each figure or table.

~~~
# abd
~~~

#Fig Figure example {#fig1#}

```python hide-input
%matplotlib inline
import matplotlib.pyplot as plt
plt.plot([5, 13, 3]);
```

#Tab DataFrame {#tab1#}

```python hide-input
import pandas as pd
pd.DataFrame([[1, 2], [3, 4]], columns=list('ab'))
```

Figure {#fig1#}, Table {#tab1#}

Link {#matplotlib#}

Line {#bokeh#}

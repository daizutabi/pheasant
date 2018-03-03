# Pheasant

## Overview

Pheasant is a Markdown converter which is designed to be used as a plugin for static site generators such as [MkDocs](http://www.mkdocs.org/) or [Pelican](http://docs.getpelican.com/en/stable/).

Highlights include:

+ Auto generation of outputs for a fenced code block or inline code in Markdown source using [Jupyter client](https://jupyter-client.readthedocs.io/en/stable/). The code language is not restricted to Python.
+ Auto numbering of headers, figures, and tables. Numbered objects can be linked from Markdown source.
+ [Windows only] Extract shapes from Microsoft PowerPoint presentations.
+ Simple interface to use Pheasant as a plugin for other site generators.
+ Easy to introduce any extensions you want to Pheasant.


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
PHEASANT = {'jupyter': {'enabled': True}, 'number': {'enabled': True}}
~~~

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

after execution of `print` function via Jupyter client and finally rendered as:

```python
print(1)
```

"Inline code" can also be converted. For example:

~~~
```python
name = 'Pheasant'
```
~~~

```python hide
name = 'Pheasant'
```

Then, `"My name is {{#name}}."` becomes "My name is {{name}}." You can assign a variable in an inline code. `"{{#a=5}}$2a$ is equal to {{#2*a}}."` becomes "{{a=5}}$2a$ is equal to {{2*a}}." Note that an inline code without outputs is not shown after conversion.

Pheasant supports various output formats other than standard stream. For example, you can create a PNG image from Matplotlib.

~~~
```python
import matplotlib.pyplot as plt
plt.plot([1, 3, 2])
```
~~~

The above Markdown source creates an input Python code block and a PNG image:

```python
import matplotlib.pyplot as plt
plt.plot([1, 3, 2])
```

You may want to display only graphics. You can use `display` option for a fenced code.

~~~
```python display
plt.plot([1, 3, 2])
```
~~~

This creates only a PNG image without a code block like below:

```python display
plt.plot([1, 3, 2])
```

!!! Note
    Matplotlib package already has been imported in the previous code block so that we don't need to import it again here.

Pheasant also supports Bokeh's HTML output.



~~~
```python hide
from bokeh.plotting import figure
from bokeh.embed import components

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
```

{{plot}}
~~~



```python hide
from bokeh.plotting import figure
from bokeh.embed import components

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
```

{{plot}}

The language executed in Pheasant is not restricted to Python. For example,
if you install Julia kernel, you can write:


~~~
```julia
x = 2
println(3x)
```
~~~

to get an output like below:


```julia
>>> x = 2
>>> println(3x)
6
```

### Auto numbering of headers, figures, and tables.

As you can see, all of headers are numbered in this document. This is done by Pheasant automatically. In addition, Pheasant can count the number of figures and tables and give the identical number to each figure or table.

You can use a special *header* statement for figure (`#Figure`) and table (`#Table`) to number them like below:

~~~
#Figure This is a cat. {#cat#} <= BUG!

![jpg](img/cat.jpg)
~~~

#Fig This is a cat. {#cat#}

![jpg](img/cat.jpg)

!!! Note
    In the above Markdown source, `{#<tag>#}` is a tag for hyperlink described below.

Off course, you can use any code to create a figure:

~~~
#Fig A Matplotlib figure

```python hide
plt.plot([3, 2])
```
~~~

#Fig A Matplotlib figure

```python hide
plt.plot([3, 1])
```

Like figures, tables can be numbered.

~~~
#Table A Markdown table

a | b
--|--
0 | 1
2 | 3
~~~

#Table A Markdown table

a | b
--|--
0 | 1
2 | 3

Pandas DataFarme is useful to create a table programmatically.

~~~
#Table A Pandas DataFrame

```python hide
import pandas as pd
pd.DataFrame([[1, 2], [3, 4]], columns=list('ab')) * 2
```
~~~


#Table A Pandas DataFrame

#begin
```python hide
import pandas as pd
pd.DataFrame([[1, 2], [3, 4]], columns=list('ab')) * 2
```
#end

A Markdown source for figures and tables is a source block separated by a blank line from following text. If a figure or table has a blank line within it, you have to explicitly show the content range with `#begin` and `#end` statement.

~~~
#Fig A Bokeh's HTML figure

#begin
```python inline
{{plot}}
```
#end
~~~

#Fig A Bokeh's HTML figure

#begin
```python inline
{{plot}}
```
#end

### Hyperlink

Numbered objects are linked from Markdown source using `{#<tag>#}`:

~~~
For example, go to Fig. {#cat#}
~~~

For example, go to Fig. {#cat#}

# test

```python run
from IPython import get_ipython
ip = get_ipython()
ip.display_formatter.formatters
```

```python
from bokeh.plotting import figure

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 3, 3, 2, 4], size=10)
plot.__class__
```

```python
def func(obj):
  print(obj)
  return "121", {"key": 124}

html_formatter = ip.display_formatter.formatters['text/html']
html_formatter.for_type(plot.__class__, func)
plot
```

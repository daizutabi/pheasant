# Bokeh

```python
import matplotlib.pyplot as plt
plt.plot([4, 2])
```

```python
from bokeh.plotting import figure
from bokeh.io import show, output_notebook
from bokeh.resources import INLINE
output_notebook(INLINE)
```

```python
plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=20)
show(plot)
```

acd {{!plot}} abc

#Figure a
<!-- begin -->
{{!plot}}
<!-- end -->

abc

# HoloViews

```python
import numpy as np
import pandas as pd
import holoviews as hv
hv.extension('bokeh')


from bokeh.io import show, output_notebook
from bokeh.resources import INLINE
output_notebook(INLINE)

xs = np.arange(-10, 10.5, 0.5)
ys = 100-xs**2

df = pd.DataFrame(dict(x=xs, y=ys))
df.head()


simple_curve = hv.Curve(df,'x','y')

fig = hv.render(simple_curve)
show(fig)

print(simple_curve)

renderer = hv.renderer('bokeh')
curve = hv.Curve(([1, 2, 3], [5, 1, 3]))


dir(curve)


png, info = renderer(curve)#, fmt='png')


png
from IPython.display import HTML
HTML('<p>abc</p]>')
```

```python
from pheasant.jupyter.display import display

display(simple_curve)
```

{{ display(curve) }}

{{ renderer(curve, fmt='svg')[0]}}

{{ curve }}

```python
df = pd.DataFrame([[1 ,2]])
```

{{df}}

![python](hello.func)

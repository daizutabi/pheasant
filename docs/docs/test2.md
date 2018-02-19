# HoloViews

```python
## holoviews_backend=matplotlib
import holoviews as hv
renderer = hv.renderer('matplotlib')
curve = hv.Curve(([1, 2, 3], [5, 1, 3]))
png, info = renderer(curve, fmt='png')

from IPython.display import display_png
display_png(png, raw=True)
```

```python
from pheasant.jupyter.display import display

display(curve)
```

{{ display(curve) }}

{{ renderer(curve, fmt='svg')[0]}}

{{ curve }}

```python
df = pd.DataFrame([[1 ,2]])
```

{{df}}

![python](hello.func)

# Test

```python hide
from bokeh.plotting import figure
plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=20)
```

{{!plot}}


```python hide
import numpy as np
import pandas as pd
import holoviews as hv
hv.extension('bokeh')
```

```python display
xs = np.arange(-10, 10.5, 0.5)
ys = 100-xs**3
df = pd.DataFrame(dict(x=xs, y=ys))
df.head()
```

```python inline
curve = hv.Curve(df,'x','y')
{{!curve}}
```

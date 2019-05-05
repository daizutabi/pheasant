# Main

```python
import matplotlib.pyplot as plt
```

```python
plt.plot([1, 3])
```

```python
from bokeh.plotting import figure
plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
plot
```

```python
import holoviews as hv
hv.Curve(((1, 2), (2, 3)))
```

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
import pandas as pd
pd.DataFrame([[1, 2], [3, 4]], index=list('XY'), columns=list('ab'))
```

```python
pd.Series([1, 2])
```

```python abc fold_frac_powers=True
import sympy
sympy.symbols("x") ** 2
```

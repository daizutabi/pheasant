# Test

```python
import holoviews as hv
import numpy as np

def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

frequencies = [0.5, 0.75, 1.0]
curve_dict = {f: sine_curve(0, f) for f in frequencies}
hv.HoloMap(curve_dict, kdims='Frequency')
```

```python
a = 1
b = 1


def func(x):
    return x


func(2)
```

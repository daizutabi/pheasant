# Image

## subection {#tag-b#}

Go to {#tag-a#}

```python
import holoviews as hv
curve = hv.Curve(([1,2], [3,4]))
curve
```

{{curve}}

HoloMap can work as in a Jupyter Notebook 6{{2*3}}6.

```python
import numpy as np

def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

frequencies = [0.5, 0.75, 1.0]
curve_dict = {f: sine_curve(0, f) for f in frequencies}
holomap = hv.HoloMap(curve_dict, kdims='Frequency')
```

{{holomap}}

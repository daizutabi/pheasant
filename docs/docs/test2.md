# Test

```python hide
import holoviews as hv
import numpy as np

frequencies = [0.5, 0.75, 1.0]

def sine_curve(phase, freq):
    xvals = [0.1* i for i in range(100)]
    return hv.Curve((xvals, [np.sin(phase+freq*x) for x in xvals]))

curve_dict = {f:sine_curve(0,f) for f in frequencies}
hmap = hv.HoloMap(curve_dict, kdims='frequency')
hmap
```

{{hmap}}



```python
curve = hv.Curve(((1, 2), (4, 5)))
curve
```

{{curve}}

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


```python
import pandas as pd
pd.Series([1,2,3])
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
import matplotlib.pyplot as plt
```

```python
def f(k):
  print(k)
  plt.plot([1, k])
  plt.show()
  print("a")
```

```python display-last
for k in range(3):
  f(k)
  print('b')
```

![jpg](img/cat.jpg)

```python
from IPython.display import Image
Image('docs/img/cat.jpg')
```

```python
Image('docs/img/cat.jpg', width=50)
```

```python
from IPython.display import Image
Image('docs/img/cvae.gif')
```

<!--break-->

abc

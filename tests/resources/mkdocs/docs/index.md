# MkDocs Example

## Stream {#section#}

```python
x = 10
print(2*x)
```

```julia
x = 31
println(3x)
```

``` python
print(1)
```

#Fig Figure example {#fig1#}

```python hide-input
%matplotlib inline
import matplotlib.pyplot as plt
plt.plot([5, 13, 3]);
```

#Tab DataFrame {#tab1#}

```python hide-input
import pandas as pd
pd.DataFrame([[1, 2], [3, 4]], columns=list('ab'))
```

Figure {#fig1#}, Table {#tab1#}

Link {#matplotlib#}

Line {#bokeh#}


## HoloViews

```python hide
import holoviews as hv
hv.extension('bokeh')
```

あいう

```python
hv.Curve([1, 2, 3])
```

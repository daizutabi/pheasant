# Test

```python
from bokeh.plotting import figure
p = figure(title='Test', width=200, height=200)
p.xaxis.axis_label = 'Petal Length'
p.yaxis.axis_label = 'Petal Width'
p.circle([1, 2, 3], [4, 5, 6])
p
```

{{!p}}

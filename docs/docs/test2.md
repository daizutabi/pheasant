
# HoloViews
<!--
```python
import holoviews as hv
renderer = hv.renderer('bokeh')
```

```python
curve = hv.Curve(([1, 2, 3], [2, 3, 1]))
type(curve)
```

```python
hv.Store.registry['bokeh'][hv.Curve]
plot = renderer.get_plot(curve)
type(plot.state)
```

```python
from bokeh.embed import components
script, div = components(plot.state)
print(script[:131] + '...\n', div)
```

`{{#plot.state}}`

{{plot.state}}


{{script}}{{div}}



```python
html, info = renderer(curve, fmt='html')
print(html[:132] + '...\n\n', info)
```

`{{#html}}`


#Fig a

<!-- begin --> <!-- {{html}} --> <!-- end -->

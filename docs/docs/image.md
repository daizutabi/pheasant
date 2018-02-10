# Image

## Matplotlib

```python
plt.plot([1,2,3])[0]
```
{{'d'}}

```python
## inline
plt.plot([1, 2, 4])
{{plt.gcf()}}
```

{{plt.plot([1, 2, 4]);plt.gca()}}

{{pd.DataFrame([[1,3]])}}

## Bokeh

You can embed plots into MkDocs HTML documents. Following [User Guide "Embedding Plots and Apps"](https://bokeh.pydata.org/en/latest/docs/user_guide/embed.html) from official Bokeh documents, configure your `mkdocs.yml` as below:

```yml
extra_css:
  - https://cdn.pydata.org/bokeh/release/bokeh-0.12.14.min.css
  - https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.14.min.css
  - https://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.14.min.css

extra_javascript:
  - https://cdn.pydata.org/bokeh/release/bokeh-0.12.14.min.js
  - https://cdn.pydata.org/bokeh/release/bokeh-widgets-0.12.14.min.js
  - https://cdn.pydata.org/bokeh/release/bokeh-tables-0.12.14.min.js
```

Here, `0.12.14` is a version number of Bokeh and you can choose other version number you want to use.

In order to embed a plot in your document, `bokeh.embed.components` function can be used. This function returns `<script>`  and `<div>` tags. For example:

```python
from bokeh.plotting import figure
from bokeh.embed import components

plot = figure(plot_width=250, plot_height=250)
plot.circle([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], size=10)
script, div = components(plot)
print(script[:132] + '...\n', div)
```

These `<script>`  and `<div>` tags are used in inline code of `{{#script}}{{#div}}` to get a plot as shown below:

`{{#script}}{{#div}}`
{{script}}{{div}}

A short cut to this functionality is prepared.

`{{#plot}}`

{{plot}}

#Code hello.func

from pheasant.jupyter.client import Jupyter
jupyter = Jupyter()

source = """
# Test
```python
a = 1
```
{{a}}
XX`{{#a}}`YY

"""



print(jupyter.converter.convert(source))

from pheasant.number.client import Number
number = Number()

source = """
# Test

```python
a = 1
```
{{a}}
XX`{{#a}}`YY

"""

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

number.on_page_read_source('ded')


gen = number.renderer.parse(source)

next(gen)

number.converter.coro

list(gen)
number.header_kind
number.config

number.renderer.pattern.findall(source)



def coro(source):
    for s in source:
        yield from f(s)

d = coro([1,2,3])

def f(s):
    yield s
    x = g()
    yield s
    yield s

def g():
    return next(d)

next(d)

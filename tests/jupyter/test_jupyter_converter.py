from pheasant.jupyter.converter import Jupyter

converter = Jupyter()

source = """
text
```python
a = 1
```
>>{{a}}<<
~~~
```python
print(1)
```
~~~
text
```python inline
a = {{2*3}}
```

{{a}}


"""


for a in converter.parse(source):
    print(a)

print('----------------------------')
print(converter.convert(source))

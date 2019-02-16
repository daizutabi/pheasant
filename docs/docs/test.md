# Test

```python inline
df = pd.DataFrame([[4, 2], [3, 4]], columns=['a', 'b'])

def func(x):
  plt.cla()
  plt.plot([0, x, 2*x])

  return {{^plt.gca()}}

df = df.applymap(func)
```

{{df}}

```python
df
```


![python](hello.func)

~~~python
print(3)
print(2)

def func(x):
    return 2 * x
~~~

abcde

#Tab. a html table

First Header | Second Header
------------ | -------------
Content Cell | Content Cell
Content Cell | Content Cell

#Tab. a DataFrame table

<!-- begin -->
```python
## inline
df = pd.DataFrame([[1, 2]])
{{df}}
```
<!-- end -->


$$a^3\int f(x)dx$$

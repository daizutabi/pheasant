# Test

```python
b = 4
b
```

acd {{a=1}}{{a}} cde {{b}}

```python
## inline
plt.plot([1, 2, 3])
{{plt.gca()}}
```

```python
## inline
df = pd.DataFrame([[1, 2], [3, 4]], columns=['a', 'b'])

def func(x):
  plt.cla()
  plt.plot([0, x, x**2])
  return {{^plt.gca()}}

{{df.applymap(func)}}
```

#Code hello.func

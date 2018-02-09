# Test

```python
b = 9
b
```

acd {{a=1}}{{a}} cde {{b}}

```python
## inline
plt.plot([1, 3, 4])
{{plt.gca()}}
```

```python
## inline
df = pd.DataFrame([[5, 0], [3, 4]], columns=['a', 'b'])

def func(x):
  plt.cla()
  plt.plot([0, x, 3*x])
  return {{^plt.gca()}}

{{df.applymap(func)}}
```

#Code hello.func

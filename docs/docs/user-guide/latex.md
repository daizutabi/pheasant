# LaTeX
```python
import sympy
```

```python
x = sympy.Symbol('x')
x**5
```

#Eq {{x**3+2*x}} + {{x}}

$${{x**2}}$$


<!-- break -->

```python
from pheasant.renderers.jupyter.sympy import sympy_matrix
N, n, m = 3, 2, 4
Y = sympy_matrix('y', N, m)
```

```python debug
Y
```

$${{Y}}$$


```python
from pheasant.core.array import Matrix, Vector, partial, ones
N, n, m = 3, 2, 4
Y = Matrix('y', N, m)
X = Matrix('x', N, n)
W = Matrix('w', n, m)
B = Vector('b', m)
```

```python debug
Y
```

~~~
$$
{{Y}}={{X}}\cdot{{W}} \\ + {{ones(N, 1)}}\cdot{{B}}
$$
~~~


$$
{{Y}}={{X}}\cdot{{W}} \\ + {{ones(N, 1)}}\cdot{{B}}
$$


```python text
import sympy as sp
import numpy as np
sp.init_printing()

xw = np.array([[11, 12, 13, 14], [21, 22, 23, 24], [31, 32, 33, 34]])
b = np.array([1000, 2000, 3000, 4000])
sp.Matrix(xw + np.ones((3, 1), int) @ b.reshape((1, -1)))
```

```python
sp.Matrix(xw + b)
```

```python text
x = sp.Symbol('x')
x ** 3
```

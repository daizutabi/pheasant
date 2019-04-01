# Sympy

First, import the Sympy package.

```python
import sympy
```

## Basic usage

Sympy symbols or expressions in a fenced code block are automatically rendered in display mode:

```python
x = sympy.Symbol('x')
x**5
```

On the other hand, in an inline code, a Sympy object just returns a latex string like this `{{#x**2}}` = {{x**2}}. This is intentional behavior. You can choose inline mode or display mode. Furthermore, you can form an expression you want.

~~~copy
* This is an inline code example: ${{x**2+x+1}}$
~~~

~~~copy
* This is a display code example:

$${{x**2+x+1}}$$
~~~

~~~copy
* You can concatenate Sympy objects to make a expression in a form you want:

$${{x**2}} - {{x}} + {{x}}$$
~~~

## Matrix

```python
import numpy as np

xw = np.array([[11, 12, 13, 14], [21, 22, 23, 24], [31, 32, 33, 34]])
b = np.array([1000, 2000, 3000, 4000])
sympy.Matrix(xw + np.ones((3, 1), int) @ b.reshape((1, -1)))
```

```python
from pheasant.renderers.jupyter.sympy import sympy_matrix
sympy_matrix('y', 2, 3)
```

<!-- break -->
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

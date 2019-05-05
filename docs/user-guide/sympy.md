# SymPy and LaTeX

First, import the SymPy package.

```python
import sympy
```

## Basic usage

SymPy symbols or expressions in a fenced code block are automatically rendered in display mode:

```python
x = sympy.Symbol('x')
x**3
```

On the other hand, in an inline code, a SymPy object just returns a latex string like this `{{#x**2}}` = {{x**2}}. This is intentional behavior. You can choose inline mode or display mode.

~~~copy
This is an inline mode example: ${{x**2+1/x+1}}$
~~~

~~~copy
This is a display mode example:

$${{x**2+1/x+1}}$$
~~~

You can concatenate SymPy objects and/or normal latex source in the same line to make an expression form you prefer:

~~~copy
$${{x**2}} - {{x}} + {{x}} + \frac1y$$
~~~

Here, $-{{x}}+{{x}}$ does not cancel out automatically.

## LatexPrinter

You can pass keyward arguments to [LatexPrinter](https://docs.sympy.org/latest/modules/printing.html?highlight=latex#module-sympy.printing.latex) by **"commented filter"** notation.

~~~copy
`fold_short_frac` option: Emit `p/q` instead of `\frac{p}{q}`

Example: ${{1/x}}$ vs. ${{1/x # fold_short_frac=True}}$
~~~

In a fenced code block, you can use normal option notation:

~~~copy
```python fold_frac_powers=True
x**sympy.Rational(2, 3)
```
~~~

## Numbering

Pheasant uses MathJax's [Automatic Equation Numbering](http://docs.mathjax.org/en/latest/tex.html#automatic-equation-numbering). Use the custom header syntax like the figure and table. Also, you can add a tag for link.

~~~
#Eq f(x) = {{x**2}} {##eq-a#}
~~~

#Eq f(x) = {{x**2}} {#eq-a#}

Using starred form, the equation won’t be numbered like original LaTeX.

~~~copy
#Eq* f(x) = {{x**2}}
~~~

~~~
As usual, you can refer to equation: See Eq. {##eq-a#}
~~~

As usual, you can refer to equation: See Eq. {#eq-a#}

Also, you can use native latex syntax. From MathJax document:

~~~copy
In equation \eqref{eq:sample}, we find the value of an interesting integral:

#Eq \int_0^\infty \frac{x^3}{e^x-1}\,dx = \frac{\pi^4}{15} \label{eq:sample}
~~~

## LaTeX utility function

For convenience, Pheasant prepares some utility functions.

### #subscript
```python
from pheasant.utils import latex as L
print(L.subscript("x", 1))
print(L.subscript("y", "i"))
```

### #row
```python
print(L.row("a", 3))
print(L.row("b", 3, 4))
print(L.row("c", 3, 4, transpose=True))
```

### #matrix
```python
print(L.matrix("x", 2, 3))
```
```python
print(L.matrix("x", 2, 3, mat_delim="("))
```
```python
print(L.matrix("x", 2, 3, transpose=True))
```

### #sympy_matrix
```python
L.sympy_matrix("x", 2, 3)
```

### #const, ones, zeros
```python
print(L.const(1, 2, 3))
```
```python
print(L.ones(2, 3))
```
```python
print(L.zeros(2, 3))
```

### #vector
```python
print(L.vector("v", 4))
```
```python
print(L.vector("u", 4, transpose=True, mat_delim="("))
```

### #partial
```python
print(L.partial("f", "x"))
```
```python
print(L.partial("f", "x", frac=True))
```

### #Matrix
```python
X = L.Matrix("x", 3, 2)
X
```
```python
print(X)
```
```python
print(X.T)
```
```python
X.S  # sympy.Matrix
```
```python
print(X.partial("f"))
```
```python
print(X.partial("f", frac=True))
```
```python
print(X.spartial("f"))
```

### #Vector
```python
V = L.Vector("v", 2)
V
```
```python
print(V)
```
```python
print(V.T)
```
```python
V.S  # sympy.Matrix
```
```python
print(V.partial("f"))
```
```python
print(V.partial("f", frac=True))
```
```python
print(V.spartial("f"))
```

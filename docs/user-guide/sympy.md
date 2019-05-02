# SymPy

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

On the other hand, in an inline code, a SymPy object just returns a latex string like this `{{#x**2}}` = {{x**2}}. This is intentional behavior. You can choose inline mode or display mode. Furthermore, you can form an expression you want.

~~~copy
* This is an inline mode example: ${{x**2+x+1}}$
~~~

~~~copy
* This is a display mode example:

$${{x**2+x+1}}$$
~~~

* You can concatenate SymPy objects and/or normal latex source in the same line to make an expression form you want:

~~~copy
$${{x**2}} - {{x}} + {{x}} + \frac1y$$
~~~

Here, $-{{x}}+{{x}}$ does not cancel out automatically.

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
